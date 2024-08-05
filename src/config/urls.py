from django.contrib import admin
from django.urls import path, include


handler404 = "core.util.page_not_found_view"
handler500 = "core.util.page_error_view"

urlpatterns = [
    path("admin/", admin.site.urls),

    # Traditional django urls
    # Add any custom URL'S below this
    # path("my-custom-url/", include("myapp.urls")),

    # abcdjango magic urls : use abc ContextManager View
    path("", include("core.urls")),
]