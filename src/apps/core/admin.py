from django.contrib import admin
from .models import Nav, Link, App, Module


@admin.register(Nav)
class NavAdmin(admin.ModelAdmin):
    pass


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "link",
        "nav",
        "order",
    )


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    pass

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    pass