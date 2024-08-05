from django.contrib import auth
from core.util import (
    debug,
    HttpResponseForbidden,
    render,
    redirect,
    AuthRequired,
    ContextManager,
)


class Logout(AuthRequired, ContextManager):
    def post(self, request):
        request.session["user_token"] = "0"
        self.context["javascript"].append("js/auth/logout.js")
        auth.logout(request)
        return render(request, "src/logout.html", self.context)

    def get(self, request):
        return HttpResponseForbidden(request)


class Login(ContextManager):
    def post(self, request):
        user = auth.authenticate(
            username=request.POST["email"], password=request.POST["password"]
        )
        if user is not None:
            auth.login(request, user)
            next = request.session.pop("next")
            return redirect(next)
        else:
            debug(request, pop=True, msg="O_O")
            return render(request, "src/login.html", self.context)

    def get(self, request):
        if "next" in request.GET:
            request.session["next"] = request.GET["next"]
        else:
            request.session["next"] = "/"

        return render(request, "src/login.html", self.context)
