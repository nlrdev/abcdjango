from core.util import (
    debug,
    JsonResponse,
    render,
    ContextManager,
    page_not_found_view,
    copy,
)

class WebSite(ContextManager):
    def post(self, request):
        try:
            return JsonResponse(self.context)
        except Exception as e:
            debug(request, log=True, e=e)
            return JsonResponse({"error": e})


    def get(self, request):
        try:          
            return render(request, "website/index.html", request.context)
        except Exception as e:
            debug(request, log=True, e=e)
            return page_not_found_view(request, e)
