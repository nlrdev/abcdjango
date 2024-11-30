import bleach
from core.util import logger


class ContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            logger.error(e)
        

    def process_view(self, request, view_func, view_args, view_kwargs):
        url_vars = request.resolver_match.kwargs if request.resolver_match else {}
        request.app = bleach.clean(view_kwargs.get("app", "website"))
        request.module = bleach.clean(view_kwargs.get("module", "default"))
        request.page = bleach.clean(view_kwargs.get("page", "index"))

        print(request.app)
        print(request.module)
        print(request.page)

        if request.POST.get("action"):
            request.action = bleach.clean(request.POST.get("action"))
        else:
            request.action = request.page

        if request.POST.get("tag"):
            request.tag = bleach.clean(request.POST.get("tag"))
        else:
            request.tag = None

        if request.POST.get("uid"):
            request.uid = bleach.clean(request.POST.get("uid"))
        else:
            request.uid = None

        request.current_page = bleach.clean(request.path.split("/")[-2])
        request.context = {
            "current_page": request.current_page if request.current_page else "home",
            "app": request.app,
            "module": request.module,
            "page": request.page,
            "app_path": f"{request.app}/index.html",
            "module_path": f"{request.app}/{request.module}/{request.page}.html",
            "javascript": [
                f"js/{request.app}/{request.module}.js",
            ],
            "css": [
                "css/main.css",
            ],
        }