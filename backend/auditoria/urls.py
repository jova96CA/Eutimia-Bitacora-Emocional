from django.urls import path
from .views import Auditoria, MonitorIA
urlpatterns = [path("admin/auditoria/", Auditoria.as_view()), path("admin/monitor/ia/", MonitorIA.as_view())]
