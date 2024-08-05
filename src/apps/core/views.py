from importlib import import_module
from .util import render, debug, page_error_view, page_not_found_view
from core.models import App




def dynamic_view_loader[HttpResponse](request, app="website", module="default", page="index"):    
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
