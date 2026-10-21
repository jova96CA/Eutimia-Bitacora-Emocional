from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from cuentas.models import Usuario
from cuentas.permissions import EsAdministrador
from auditoria.servicios import registrar

def resumen(u): return {"id": u.id, "nombre": u.first_name, "email": u.email, "rol": u.rol, "is_active": u.is_active, "date_joined": u.date_joined, "num_registros": u.registros.count()}
class Usuarios(APIView):
    permission_classes = [EsAdministrador]
    def get(self, request):
        qs = Usuario.objects.annotate(_n=Count("registros"))
        q = request.query_params.get("q", "")
        if q: qs = qs.filter(first_name__icontains=q) | qs.filter(email__icontains=q)
        activo = request.query_params.get("activo")
        if activo in ("true", "false"): qs = qs.filter(is_active=(activo == "true"))
        return Response([resumen(u) for u in qs.order_by("id")])
    def post(self, request):
        nombre, email = request.data.get("nombre", ""), str(request.data.get("email", "")).lower()
        password = request.data.get("password", "")
        try: validate_password(password)
        except ValidationError as exc: return Response({"detail": exc.messages}, status=400)
        if not nombre or not email or Usuario.objects.filter(email=email).exists(): return Response({"detail": "Nombre y correo único requeridos"}, status=400)
        u = Usuario.objects.create_user(username=email, email=email, first_name=nombre, password=password, rol="usuario")
        registrar("admin", "usuario_creado", "ok", request.user, u.id)
        return Response(resumen(u), status=201)

class UsuarioDetalle(APIView):
    permission_classes = [EsAdministrador]
    def patch(self, request, pk):
        try: u = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist: return Response(status=404)
        if u.pk == request.user.pk and request.data.get("is_active") is False: return Response({"detail": "No puedes desactivarte"}, status=400)
        if "nombre" in request.data: u.first_name = request.data["nombre"]
        if "email" in request.data:
            email = request.data["email"].lower()
            if Usuario.objects.exclude(pk=pk).filter(email=email).exists(): return Response({"detail": "Correo ya registrado"}, status=400)
            u.email = email; u.username = email
        if "is_active" in request.data:
            active = bool(request.data["is_active"])
            if not active and u.rol == "administrador" and Usuario.objects.filter(rol="administrador", is_active=True).count() <= 1: return Response({"detail": "Debe quedar un administrador activo"}, status=400)
            u.is_active = active
        u.save()
        registrar("admin", "usuario_desactivado" if not u.is_active else "usuario_actualizado", "ok", request.user, u.id)
        return Response(resumen(u))
    def delete(self, request, pk):
        try: u = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist: return Response(status=404)
        if u.pk == request.user.pk: return Response({"detail": "No puedes eliminarte"}, status=400)
        if u.rol == "administrador" and Usuario.objects.filter(rol="administrador", is_active=True).count() <= 1: return Response({"detail": "Debe quedar un administrador activo"}, status=400)
        ident = u.id; u.delete(); registrar("admin", "usuario_eliminado", "ok", request.user, ident); return Response(status=204)

class AsignarRol(APIView):
    permission_classes = [EsAdministrador]
    def post(self, request, pk):
        try: u = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist: return Response(status=404)
        rol = request.data.get("rol")
        if rol not in ("usuario", "administrador"): return Response({"detail": "Rol no válido"}, status=400)
        if u.pk == request.user.pk and rol != "administrador": return Response({"detail": "No puedes quitarte el rol"}, status=400)
        if rol != "administrador" and u.rol == "administrador" and u.is_active and Usuario.objects.filter(rol="administrador", is_active=True).count() <= 1: return Response({"detail": "Debe quedar un administrador activo"}, status=400)
        u.rol = rol
        if rol == "administrador": u.is_staff = True
        elif not u.is_superuser: u.is_staff = False
        u.save(); registrar("admin", "rol_asignado", "ok", request.user, u.id, detalle=rol)
        return Response(resumen(u))
