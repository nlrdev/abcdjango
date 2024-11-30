from importlib import import_module
from .util import get_object_or_404, debug, page_error_view, page_not_found_view
from core.models import App


def dynamic_view_loader[HttpResponse](request, app=None, module=None, page=None):
    try:
        _app = get_object_or_404(App, app_name=request.app)
        return getattr(import_module(f"{_app.app_name}.views"), _app.cls_name).as_view()(request)
    except Exception as e:
        debug(request, log=True, e=e)
        return page_not_found_view(request, e)
