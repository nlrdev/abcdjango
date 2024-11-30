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
        
    def no_context[dict](*args, **kwargs):
        return {}

    def post(self, request):
        try:
            module = get_object_or_404(Module, app__app_name=request.app, url_name=request.module)
            request.context |= getattr(import_module(f"{request.app}.ajax"), f"{module.cls_name}Ajax")()(request)
            return super(ContextManager, self).post(request)
        except Exception as e:
            raise e

    def get(self, request):
        try:
            module = get_object_or_404(Module, app__app_name=request.app, url_name=request.module)
            request.context |= getattr(import_module(f"{request.app}.context"), f"{module.cls_name}Context")()(request)
            return super(ContextManager, self).get(request)
        except Exception as e:
            raise e



class Callable(object):
    def __call__[dict](self: object, request: dict):
        return getattr(self, request.action)(request)


class AuthRequired(object):
    @method_decorator(login_required(login_url="/login/"))
    def dispatch(self, request, *args, **kwargs):
        return super(AuthRequired, self).dispatch(request, *args, **kwargs)


class StaffRequired(object):
    @method_decorator(login_required(login_url="/login/"))
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequired, self).dispatch(request, *args, **kwargs)


def get_msgs[dict](request):
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


def is_ajax[bool](request):
    return (
        True if request.headers.get("x-requested-with") == "XMLHttpRequest" else False
    )


def is_post[bool](request):
    return True if request.method == "POST" else False


def is_get[bool](request):
    return True if request.method == "GET" else False


def forbidden():
    return HttpResponseForbidden()


def time():
    now = datetime.now()
    return now.strftime("%y/%m/%d %H:%M:%S.%f")


def deserialize_form[dict](data):
    return dict(i.split("=") for i in data.split("&"))


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
