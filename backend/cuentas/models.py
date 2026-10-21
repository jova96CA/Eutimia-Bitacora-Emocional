from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        USUARIO = "usuario", "Usuario"
        ADMINISTRADOR = "administrador", "Administrador"
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.USUARIO)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.rol = self.Rol.ADMINISTRADOR
            self.is_staff = True
        super().save(*args, **kwargs)
