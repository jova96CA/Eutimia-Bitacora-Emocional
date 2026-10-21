from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

def servir(raiz):
    def vista(request, path=""):
        return serve(request, path or "index.html", document_root=raiz)
    return vista

urlpatterns = [path("django-admin/", admin.site.urls), path("api/v1/", include("config.api_urls"))]
if settings.DEBUG:
    urlpatterns += [re_path(r"^panel/(?P<path>.*)$", servir(settings.FRONTEND_ADMIN_DIR)), re_path(r"^(?P<path>.*)$", servir(settings.FRONTEND_CLIENTE_DIR))]
