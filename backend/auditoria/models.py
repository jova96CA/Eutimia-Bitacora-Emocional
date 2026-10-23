from django.conf import settings
from django.db import models


class EventoAuditoria(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    categoria = models.CharField(
        max_length=20,
        choices=[
            ("sesion", "Sesión"),
            ("admin", "Administración"),
            ("sistema", "Sistema"),
        ],
    )
    accion = models.CharField(max_length=40)
    resultado = models.CharField(
        max_length=20,
        choices=[("ok", "Correcto"), ("denegado", "Denegado"), ("fallo", "Fallo")],
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="eventos_actor",
    )
    objetivo_id = models.IntegerField(null=True, blank=True)
    referencia = models.CharField(max_length=50, blank=True)
    detalle = models.CharField(max_length=200, blank=True)
