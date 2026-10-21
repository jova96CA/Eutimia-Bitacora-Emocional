from django.conf import settings
from django.db import models

class AnalisisLog(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    valido = models.BooleanField(default=False)
    num_tokens = models.IntegerField(default=0)
    tipos_token = models.JSONField(default=dict)
    estructura = models.JSONField(default=dict)
    codigos_error = models.JSONField(default=list)

class SolicitudIA(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=20, choices=[("pendiente", "Pendiente"), ("completada", "Completada"), ("fallida", "Fallida")])
    tiempo_ms = models.IntegerField(null=True, blank=True)
    esquema_valido = models.BooleanField(null=True, blank=True)
    error_tipo = models.CharField(max_length=20, blank=True)
