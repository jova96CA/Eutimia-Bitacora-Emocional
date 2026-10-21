from django.urls import path
from .views import RegistroListaCrear, RegistroDetalle, Estadisticas, Racha, Alerta, Recursos
urlpatterns = [path("registros/", RegistroListaCrear.as_view()), path("registros/<int:pk>/", RegistroDetalle.as_view()), path("estadisticas/", Estadisticas.as_view()), path("racha/", Racha.as_view()), path("alerta/", Alerta.as_view()), path("recursos-apoyo/", Recursos.as_view())]
