from django.urls import include, path

urlpatterns = [path("", include("cuentas.urls")), path("", include("emociones.urls")), path("", include("analizador.urls")), path("", include("auditoria.urls"))]
