from django.urls import path
from .views import AnalizarLinea, MonitorAnalizador
urlpatterns = [path("interprete/analizar/", AnalizarLinea.as_view()), path("admin/monitor/analizador/", MonitorAnalizador.as_view())]
