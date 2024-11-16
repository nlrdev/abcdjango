# abcDjango

In this example the 'view' renders an appropriate response, HTTP, JSON, etc. The 'view logic' code that builds the context for the response is abstracted to static class methods that inject the context into the view dispatch, post, get, etc methods higher up in the method resolution order.


## URL's

All URLs are sent to the view loader function. The app's views and static class hierarchy determine valid routing, routes that don't exist throw a key error and the user is sent to an error page.

### URL Patterns

    path("", dynamic_view_loader, name="site"),
    path("<slug:app>/", dynamic_view_loader, name="site"),
    path("<slug:app>/<slug:module>/", dynamic_view_loader, name="site"),
    path("<slug:app>/<slug:module>/<slug:page>/", dynamic_view_loader, name="site"),

The following will load the [test] apps view with the default module and the index function.

    domain.tld/test

This will load the test view again but with the [site] module and the index function.

    domain.tld/test/site

Same as the above but with the [page] function.

    domain.tld/test/site/page

These URL slugs are passed to the dynamic_view_loader as seen below.

### Loading the Views

The "dynamic_view_loader" function will take the first argument in the URL path and then call the appropriate class-based view. Then call said view function and return the resulting HTTP Response.

    def dynamic_view_loader[HttpResponse](request, app=None, module=None, page=None):
        if app is None:
            app = "website"

        if module is None:
            module = "default"

        if page is None:
            page = "index"

        try:
            _app = get_object_or_404(App, app_name=app)
            return getattr(import_module(f"{_app.app_name}.views"), _app.cls_name).as_view()(request, app, module, page)
        except Exception as e:
            debug(request, log=True, e=e)
            return page_not_found_view(request, e)


## VIEWS

Each app in this example contain a single class-based view that extends ContextManager, and ContextManager extends View. Extending View allows us all the functionality of a standard Django class-based view.

### Class-based views

Example below is returning JSON for AJAX/POST queries and using render to load templates for GET requests. A standard class-based view extending ContextManager.

    class WebSite(ContextManager):
        def post(self, request):
            try:
                return JsonResponse(self.context)
            except Exception as e:
                debug(request, log=True, e=e)
                return JsonResponse({"error": e})


        def get(self, request):
            try:
                return render(request, "website/index.html", self.context)
            except Exception as e:
                debug(request, log=True, e=e)
                return page_not_found_view(request, e)

### ContextManager

The ContextManager executes before its concrete implementation. In the dispatch method, all user input is cleaned and a context dictionary is created. The post and get methods dynamically import the required static classes. This works by using `getattr` to invoke the `__call__` method on the static class. 

    class ContextManager(View):
        def dispatch(self, request, app=None, module=None, page=None):
            if app is not None:
                self.app = bleach.clean(app)
            if module is not None:
                self.module = bleach.clean(module)
            if page is not None:
                self.page = bleach.clean(page)
            if request.POST.get("action"):
                self.action = bleach.clean(request.POST.get("action"))
            else:
                self.action = self.page

            self.context = {
                "current_page": request.path.split("/")[-2],
                "app": self.app,
                "module": self.module,
                "page": self.page,
                "app_path": f"{self.app}/index.html",
                "module_path": f"{self.app}/{self.module}/{self.page}.html",
                #"main_nav": Link.objects.filter(nav__name__contains=app),
                #"module_nav": Link.objects.filter(nav__name__contains=self.module),
                #"page_nav": Link.objects.filter(nav__name__contains=self.page),
                "javascript": [
                    f"js/{app}/{self.module}.js",
                ],
                "css": [
                    "css/main.css",
                ],
            }

            return super(ContextManager, self).dispatch(request)

        def post(self, request):
            try:
                module = get_object_or_404(Module, app__app_name=self.app, url_name=self.module)
                self.context = getattr(import_module(f"{self.app}.ajax"), f"{module.cls_name}Ajax")()(self)
                return super(ContextManager, self).post(request)
            except Exception as e:
                raise e

        def get(self, request):
            try:
                module = get_object_or_404(Module, app__app_name=self.app, url_name=self.module)
                self.context = getattr(import_module(f"{self.app}.context"), f"{module.cls_name}Context")()(self)
                return super(ContextManager, self).get(request)
            except Exception as e:
                raise e

### Callable

The static classes extend Callable, when the `__call__` method is invoked we again use `getattr` function with `self.action` to call the appropriate static method passing the view as the argument.

    class Callable(object):
        def __call__[dict](self: object, cls: object):
            return getattr(self, cls.action)(cls)

### Static methods

The static methods build context dictionaries needed to create the JSON or render that template.

    class DefaultContext(Callable):
        @staticmethod
        def index[dict](view: object):
            return {
                "default": "default",
            }


    class DefaultAjax(Callable):
        @staticmethod
        def index[dict](view: object):
            return {
                "index": "index",
            }

Below is a simple example from another project, creating a context dictionary rendering HTML and sending that page over AJAX.

    class ServerManagerAjax(Callable):
        @staticmethod
        def add_server[dict](portal: object):
            page = render_to_string(
                "portal/server_manager/add_server.html",
                {
                    "server_form": ServerForm(),
                },
                portal.request,
            )
            return {
                "modal": page,
            }

Called and updated here rendering the modal.

    function add_server() {
        $.ajax({
            type: "POST",
            data: {
            action: "add_server",
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').attr("value"),
            },
            dataType: "json",
            error: function (request, error) {
            console.log(arguments);
            console.log(" Can't do because: " + error);
            alert("Oh shit, something went wrong... Check the logs");
            },
            success: function (data) {
            $("#msg_queue").append(data.msg_list);
            if (data.modal) {
                $("#modal_wrapper").html(data.modal);
                $(".modal").modal("show");
            }
            },
        });
    }

### Creating an 'App'

A manage.py command, a 'wrapper' around the Django 'startapp' command that takes 3 args and builds out the boilerplate code required for this to work. Mostly. It's not finished.

Usage:

    python manage.py addmod -a --app [app] -m --mod [module]  -f --func [function]
