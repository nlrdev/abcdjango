import abc
import copy
import logging
import json
from typing import Any
import uuid
import bleach
from abc import ABCMeta, abstractmethod
from importlib import import_module
from django.views import View
from smtplib import SMTPException
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, render_to_string
from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.contrib import messages
from datetime import datetime
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Link, Module


logger = logging.getLogger("file_logger")


class ContextManager(View, metaclass=abc.ABCMeta):
    class Meta:
        abstract = True

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
            self.action = page

        if request.POST.get("tag"):
            self.tag = bleach.clean(request.POST.get("tag"))
        else:
            self.tag = None

        if request.POST.get("uid"):
            self.uid = bleach.clean(request.POST.get("uid"))
        else:
            self.uid = None

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
        if self.context["current_page"] == None:
            self.context["current_page"] == "home"
            
        return super(ContextManager, self).dispatch(request)

    def pass_context(*args, **kwargs) -> None:
        pass

    def no_context(*args, **kwargs) -> dict:
        return {}

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


class Callable(object):
    def __call__(self: object, cls: object) -> dict:
        return getattr(self, cls.action)(cls)


class AuthRequired(object):
    @method_decorator(login_required(login_url="/login/"))
    def dispatch(self, request, *args, **kwargs):
        return super(AuthRequired, self).dispatch(request, *args, **kwargs)


class StaffRequired(object):
    @method_decorator(login_required(login_url="/login/"))
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequired, self).dispatch(request, *args, **kwargs)


def get_msgs(request):
    return render_to_string(
        "src/msgs.html",
        {"msg": get_messages(request)},
        request,
    )


def debug(request, pop=False, msg=None, tag=None, log=False, e=None):
    if pop is True and msg is not None:
        messages.info(
            request,
            message=f"{time()} : {msg}",
            extra_tags=f"{tag}",
        )
    if log is True and e is not None:
        logger.exception(e)


def is_ajax(request):
    return (
        True if request.headers.get("x-requested-with") == "XMLHttpRequest" else False
    )


def is_post(request):
    return True if request.method == "POST" else False


def is_get(request):
    return True if request.method == "GET" else False


def forbidden():
    return HttpResponseForbidden()


def time():
    now = datetime.now()
    return now.strftime("%y/%m/%d %H:%M:%S.%f")


def deserialize_form(data):
    return dict(i.split("=") for i in data.split("&"))


def send_contact_mail(request):
    name = bleach.clean(request.POST.get("name"))
    email = bleach.clean(request.POST.get("email"))
    subject = bleach.clean(request.POST.get("subject"))
    message = bleach.clean(request.POST.get("message"))
    try:
        send_mail(
            f"Message from Name:[{name}] Email:[{email}] Regarding:[{subject}]",
            f"{message}",
            "noreply@silimasoftware.com",
            ["contact@silimasoftware.com"],
        )
    except SMTPException as e:
        messages.error(
            request,
            message=f"{time()} ERROR: {e} ",
            extra_tags="danger",
        )
        return {"msg_list": get_msgs(request)}
    else:
        # submit counter
        if "support_mail_sent" in request.session:
            request.session["support_mail_sent"] += 1
        else:
            request.session["support_mail_sent"] = 1

        return {"success": "True"}


def page_not_found_view(request, exception):
    context = {
        "module_path": "src/404.html",
        "css": [
            "css/main.css",
        ],
    }
    return render(request, "website/index.html", context, status=404)


def page_error_view(request):
    context = {
        "module_path": "src/404.html",
        "css": [
            "css/main.css",
        ],
    }
    return render(request, "website/index.html", context, status=500)
