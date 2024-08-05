from django.db import models


class Nav(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "core"

    def __str__(self):
        return self.name


class Link(models.Model):
    nav = models.ForeignKey(Nav, related_name="link", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="", blank=True)
    link = models.CharField(max_length=255, default="", blank=True)
    icon = models.CharField(max_length=255, default="", blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.name


class App(models.Model):
    url_name = models.CharField(max_length=255, default="", blank=True)
    app_name =  models.CharField(max_length=255, default="", blank=True)
    cls_name = models.CharField(max_length=255, default="", blank=True)

    def __str__(self):
        return self.app_name
    
    
class Module(models.Model):
    app = models.ForeignKey(App, related_name="module", on_delete=models.CASCADE)
    url_name = models.CharField(max_length=255, default="", blank=True)
    cls_name = models.CharField(max_length=255, default="", blank=True)

    def __str__(self):
        return self.url_name
    

class Function(models.Model):
    module = models.ForeignKey(Module, related_name="function", on_delete=models.CASCADE)
    url_name = models.CharField(max_length=255, default="", blank=True)
    func_name = models.CharField(max_length=255, default="", blank=True)

    def __str__(self):
        return self.url_name