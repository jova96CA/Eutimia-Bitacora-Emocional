from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Registro(models.Model):
    class Categoria(models.TextChoices):
        ANSIEDAD = "ansiedad", "Ansiedad"
        TRISTEZA = "tristeza", "Tristeza"
        ESTRES = "estres", "Estrés"
        CALMA = "calma", "Calma"
        ALEGRIA = "alegria", "Alegría"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registros"
    )
    fecha = models.DateField()
    intensidad = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    texto_libre = models.CharField(max_length=200, blank=True)
    ia_etiqueta = models.CharField(max_length=10, blank=True)
    ia_confianza = models.FloatField(null=True, blank=True)
    ia_patron_riesgo = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "fecha"], name="un_registro_por_dia"
            )
        ]
