from django.urls import path
from user.views import Logout, Login
from .views import dynamic_view_loader


urlpatterns = [
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),    
    path("", dynamic_view_loader, name="site"),
    path("<slug:app>/", dynamic_view_loader, name="site"),
    path("<slug:app>/<slug:module>/", dynamic_view_loader, name="site"),
    path("<slug:app>/<slug:module>/<slug:page>/", dynamic_view_loader, name="site"),
]


