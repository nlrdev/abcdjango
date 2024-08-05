# abcDjango


The yet-to-be-determined quality idea is... Have the 'view' purely focused on rendering an appropriate response, HTTP, JSON, etc. The 'view logic' code that builds the context for the response is abstracted to static class methods that inject the context into the views dispatch, post, get, etc methods but higher up in the method resolution order. This is a somewhat opinionated way of doing class-based views but not so much so that you are locked in, I tried to write this so that it complements Django's workflow, rather than replacing it. 

## URL's

Below is some standard Django magic that will catch all the URLs. The difference is rather than specifying every possible combination of URLs then doing this over and over for each new page and then mapping each URL to a view. Write once, and do nothing when you need to add new pages. All URLs are sent to the view loader function. The app's views and static class hierarchy determine valid routing, routes that don't exist throw a key error and the user is sent to an error page.

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

Now that we have our url we need to call a view. This "dynamic_view_loader" function will take the first argument in the URL path and then call the appropriate class-based view for that app. When the app is created using the 'addmod' command line tool (Explained later). The applications, all sub-classes and function names are stored in a database. Using this info we build a dictionary of views based on the app names. Then call said view as a view and return the resulting HTTP Response.

    def dynamic_view_loader[HttpResponse](request, app="website", module="default", page="index"):  
        app = bleach.clean(app)
        module = bleach.clean(module)
        page = bleach.clean(page)  

        app_views = App.objects.all()
        apps = {}
        if app_views:    
            for _app in app_views:
                cls = getattr(import_module(f"{_app.app_name}.views"), _app.cls_name)
                apps |= {_app.url_name: cls}

        try:
            return apps[app].as_view()(request, app, module, page)
        except KeyError as e:
            debug(request, log=True, e=e)
            return page_not_found_view(request, e)
        except Exception as e:
            debug(request, log=True, e=e)
            return page_error_view(request)


## VIEWS

Each app contains a single class-based view that extends ContextManager, and ContextManager extends View. The views have one job 'return a response'. Extending View allows us all the functionality of a standard Django class-based view but with some extra magic. For this example and in every use case I have implemented some derivative of this, I only ever needed a get and post method but it can be extended to support any HTTP method. 

### Class-based views

In the example below we are returning JSON for AJAX/POST queries and using render to load templates for GET requests. This looks like a standard class-based view implementation, again you are not locked in you can return whatever you want here.

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

I use 'app/index.html' in every app at the root of the app's template file structure. Using a modular approach when creating templates combined with Django built-in includes in the template language. This file will load a tree of templates based on the values in the context Dictionary. Then using AJAX any templates that change dynamically can be reloaded and injected into the page using render_to_string on the backend to write the HTML to a JSON response and then update on the client side with some simple JavaScript. I will get into this more down the road. First, we need to understand "ContextManager".

### ContextManager

The ContextManager parent class is doing all the heavy lifting, as I said earlier because of the 'method resolution order' any methods implemented here will execute before its concrete implementation above. In the dispatch method, all user input is cleaned and a context dictionary is created containing info such as paths for templates and static files, menus, and anything we need to build our response later. The post and get methods in ContextManager create dictionaries with all the static classes required for this app. We call our static method using a simple factory. Each static method needs to extend Callable 'explained further below'. This allows us to pass our view object directly into the static method as an argument. That method returns a new dictionary containing the context returned in the concrete implementation.

 
    class ContextManager(View):
        def dispatch(self, request, app=None, module=None, page=None):
            self.app = app
            self.module = module
            if request.POST.get("action"):
                self.action = bleach.clean(request.POST.get("action"))
            else:
                self.action = page

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
                modules, module_factory = Module.objects.filter(app__app_name=self.app), {}
                for module in modules:
                    cls = getattr(import_module(f"{self.app}.ajax"), f"{module.cls_name}Ajax")
                    module_factory |= {module.url_name: cls}
                self.context = module_factory[self.module]()(self)
                return super(ContextManager, self).post(request)
            except Exception as e:
                raise e

        def get(self, request):
            try:
                modules, module_factory = Module.objects.filter(app__app_name=self.app), {}
                for module in modules:
                    cls = getattr(import_module(f"{self.app}.context"), f"{module.cls_name}Context")
                    module_factory |= {module.url_name: cls}
                self.context = module_factory[self.module]()(self)
                return super(ContextManager, self).get(request)
            except Exception as e:
                raise e

### Callable

As mentioned this base class allows the extending class's static methods to be called from ContextManager. By extending Callable when the class's `__call__` method is invoked the `getattr` function is called that uses `self.action` to call the appropriate static method passing the view as the argument.

    class Callable(object):
        def __call__(self: object, cls: object) -> dict:
            return getattr(self, cls.action)(cls)


### Static methods

Here is where we build context dictionaries needed to build the JSON or render that template. In my use case, the default route is specified in the dynamic_view_loader. These are used the case that no URL path is presented, the home page. These defaults can be whatever you want assuming it matches an existing app using the above-mentioned methodology. My default for this example is app="website", module="default", page="index". So if the user loads my site the index method below containing the dictionary is returned as context. POST requests are much the same, however, you need to send a param in the post request containing the action/method name you are looking for.

    class DefaultContext(Callable):
        @staticmethod
        def index[dict](view: object):
            return {
                "default": "default",
            }


    class DefaultAjax(Callable):
        @staticmethod
        def index(view: object) -> dict:
            return {
                "index": "index",
            }

Below is a simple example from another project, creating a context dictionary rendering HTML servers and sending that page over AJAX.

    class ServerManagerAjax(Callable):
        @staticmethod
        def add_server(portal: object) -> dict:
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

Called and updated here rendering the model.

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
            alert("Oh shit, somthing went wrong... Check the logs");
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

This is extremely extendable and pretty powerful. I am a huge fan of server-side rending and prefer using as little JavaScript as possible. 



### Creating an 'App'

I created a manage.py command, a 'wrapper' around the Django 'startapp' command that takes 3 args and builds out the boilerplate code required for this to work. Mostly. It's not finished. 

Usage: 
   
    python manage.py addmod -a --app [app] -m --mod [module]  -f --func [function]


 




