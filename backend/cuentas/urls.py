from django.urls import path
from .views_auth import CsrfToken, RegistroCuenta, Login, LoginAdmin, Logout, Me
from . import views_admin

urlpatterns = [
    path("auth/csrf/", CsrfToken.as_view()),
    path("auth/registro/", RegistroCuenta.as_view()),
    path("auth/login/", Login.as_view()),
    path("admin/auth/login/", LoginAdmin.as_view()),
    path("auth/logout/", Logout.as_view()),
    path("auth/me/", Me.as_view()),
    path("admin/usuarios/", views_admin.Usuarios.as_view()),
    path("admin/usuarios/<int:pk>/", views_admin.UsuarioDetalle.as_view()),
    path("admin/usuarios/<int:pk>/asignar-rol/", views_admin.AsignarRol.as_view()),
]
