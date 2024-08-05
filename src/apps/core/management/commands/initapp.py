from django.core.management.base import BaseCommand
from core.models import Function, Module, App
from core.util import get_object_or_404


class Command(BaseCommand):
    def handle(self, *args, **options):
        if App.objects.filter(app_name="website").exists():
            print("App already exists!")
        else:
            app = App(
                app_name="website",
                url_name="website",
                cls_name="WebSite"
            )
            app.save()
        
        if Module.objects.filter(url_name="default").exists():
            print("Module already exists!")
        else:
            module = Module(
                app=app,
                url_name="default",
                cls_name="Default",
            )
            module.save()
            
        
        if Function.objects.filter(url_name="index").exists():
            print("Function already exists!")
        else:
            func = Function(
                module=module,
                url_name="index",
                func_name="index",
            )
            func.save()