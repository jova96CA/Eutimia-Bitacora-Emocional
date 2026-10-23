from rest_framework.permissions import BasePermission
from auditoria.servicios import registrar


def _denegacion(request, view):
    u = getattr(request, "user", None)
    if u and u.is_authenticated:
        registrar(
            "sesion",
            "permiso_denegado",
            "denegado",
            actor=u,
            detalle=view.__class__.__name__,
        )


class EsUsuario(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        permitido = bool(
            u and u.is_authenticated and u.is_active and u.rol == "usuario"
        )
        if not permitido:
            _denegacion(request, view)
        return permitido


class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        permitido = bool(
            u and u.is_authenticated and u.is_active and u.rol == "administrador"
        )
        if not permitido:
            _denegacion(request, view)
        return permitido
