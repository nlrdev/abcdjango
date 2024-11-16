import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from core.models import Function, Module, App
from core.util import get_object_or_404, logger
from config.settings import BASE_DIR


class Command(BaseCommand):
    """
        Usage:
        $python manage.py addmod app module function
        
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("-a", "--app")
        parser.add_argument("-m", "--mod")
        parser.add_argument("-f", "--func")

    def handle(self, *args, **options):
        self.APP = options["app"]
        self.MOD = options["mod"]
        self.FUNC = options["func"]
        self.app_path = os.path.join(BASE_DIR, "apps", self.APP)
        self.ajax_path = os.path.join(self.app_path, "ajax")
        self.ajax_file = os.path.join(self.ajax_path, f"{self.MOD}.py")
        self.context_path = os.path.join(self.app_path, "context")
        self.context_file = os.path.join(self.context_path, f"{self.MOD}.py")
        self.add_app()
        if Module.objects.filter(url_name=self.MOD).exists():
            logger.info(f"appending function to {self.MOD}")
            self.add_func()
        else:
            logger.info(
                f"Adding new module [{self.MOD}] and appending function [{self.FUNC}]"
            )
            self.add_module()
            self.add_func()

    def add_app(self):
        if App.objects.filter(url_name=self.APP, app_name=self.APP).exists():
            print("App already exists!")
            pass

        else:
            app = App(
                url_name=self.APP,
                app_name=self.APP,
            )
            app.save()
            if os.path.exists(self.app_path) == False:
                subprocess.run(["python", "manage.py", "startapp", self.APP])
                subprocess.run(["mv", f"./{self.APP}", "./apps"])

            template_path = os.path.join(BASE_DIR, "templates", self.APP)
            _path = Path(template_path)
            _path.mkdir(exist_ok=True)
            _path = Path(os.path.join(template_path, "index.html"))
            _path.touch(exist_ok=True)

    def add_module(self):
        if Module.objects.filter(url_name=self.MOD).exists():
            print("Module already exists!")
            pass
        else:
            module = Module(
                app=get_object_or_404(App, app_name=self.APP),
                url_name=self.MOD,
                cls_name=self.MOD.capitalize(),
            )
            module.save()
            _path = Path(self.ajax_path)
            _path.mkdir(exist_ok=True)
            _path = Path(self.context_path)
            _path.mkdir(exist_ok=True)
            _path = Path(self.ajax_file)
            _path.touch(exist_ok=True)
            _path = Path(self.context_file)
            _path.touch(exist_ok=True)

            template_path = os.path.join(BASE_DIR, "templates", self.APP, self.MOD)
            _path = Path(template_path)
            _path.mkdir(exist_ok=True)
            _path = Path(os.path.join(template_path, "index.html"))
            _path.touch(exist_ok=True)

            try:
                with open(self.context_file, "a+") as file:
                    file.write(f"{new_context_class(self.MOD)}")
                    file.close()

                with open(self.ajax_file, "a+") as file:
                    file.write(f"{new_ajax_class(self.MOD)}")
                    file.close()

                with open(os.path.join(self.ajax_path, "__init__.py"), "a+") as file:
                    file.write(f"from .{self.MOD} import {self.MOD.capitalize()}Ajax\n")
                    file.close()

                with open(os.path.join(self.context_path, "__init__.py"), "a+") as file:
                    file.write(
                        f"from .{self.MOD} import {self.MOD.capitalize()}Context\n"
                    )
                    file.close()

                with open(os.path.join(template_path, "index.html"), "a+") as file:
                    file.write(default_html())
                    file.close()

            except Exception as e:
                logger.error(e)

    def add_func(self):
        if Function.objects.filter(url_name=self.FUNC, func_name=self.FUNC).exists():
            print("Function already exists!")
            return

        func = Function(
            module=get_object_or_404(Module, url_name=self.MOD),
            url_name=self.FUNC,
            func_name=self.FUNC,
        )
        try:
            with open(self.context_file, "a+") as file:
                file.write(f"{new_func(self.FUNC)}")
                file.close()

            with open(self.ajax_file, "a+") as file:
                file.write(f"{new_func(self.FUNC)}")
                file.close()
        except Exception as e:
            logger.error(e)
        else:
            func.save()


# Static functions to generate boilerplate code for abcdjango url routing pattern thing...


def default_view_class(name):
    return f"""from core.util import (
    debug,
    JsonResponse,
    render,
    ContextManager,
    page_not_found_view,
    copy,
)

class {name.capitalize()}(ContextManager):
    def post(self, request):
        try:
            return JsonResponse(self.context)
        except Exception as e:
            debug(request, log=True, e=e)
            return JsonResponse(\u007b"error": e\u007b)


    def get(self, request):
        try:
            return render(request, "{name}/index.html", self.context)
        except Exception as e:
            debug(request, log=True, e=e)
            return page_not_found_view(request, e)

"""


def new_context_class(name):
    return f"""from core.util import Callable


class {name.capitalize()}Context(Callable):
    @staticmethod
    def index[dict](view: object):
        return \u007b
            "{name}": "{name}",
        \u007d

"""


def new_ajax_class(name):
    return f"""from core.util import Callable


class {name.capitalize()}Ajax(Callable):
    @staticmethod
    def index[dict](view: object):
        return \u007b
            "{name}": "{name}",
        \u007d

"""


def new_func(name):
    return f"""
    @staticmethod
    def {name}[dict](view: object):
        return \u007b
            "{name}": "{name}",
        \u007d

"""


def default_index():
    return """{% extends 'main.html' %} {% load static %} 
{% block content-main %}
{% if module_path %}
<div id="module_wrapper">{% include module_path %}</div>
{% endif %}
{% endblock %}

"""


def default_html():
    return """{% load static %}
<div style="padding-top:69px;">
default page O_O
</div>

"""
