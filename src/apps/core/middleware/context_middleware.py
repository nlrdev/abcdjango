import bleach
from core.util import logger


class ContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(self.create_context(request))
        except Exception as e:
            logger.error(e)
        

    def create_context(self, request):
        url_vars = getattr(request.resolver_match, "kwargs", {})
        print(url_vars)
        request.app = bleach.clean(url_vars.get("app", "website"))
        request.module = bleach.clean(url_vars.get("module", "default"))
        request.page = bleach.clean(url_vars.get("page", "index"))

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
        return request