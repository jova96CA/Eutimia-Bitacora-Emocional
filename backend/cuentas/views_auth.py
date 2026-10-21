from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistroCuentaSerializer
from .permissions import EsUsuario, EsAdministrador
from auditoria.servicios import registrar

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfToken(APIView):
    permission_classes = []; authentication_classes = []
    def get(self, request): return Response({"detail": "ok"})

@method_decorator(csrf_protect, name="dispatch")
class RegistroCuenta(APIView):
    permission_classes = []; authentication_classes = []; throttle_scope = "registro"
    def post(self, request):
        s = RegistroCuentaSerializer(data=request.data)
        if not s.is_valid(): return Response({"detail": "Los datos no son válidos", "errores": s.errors}, status=400)
        u = s.save(); registrar("admin", "usuario_creado", "ok", actor=u, objetivo_id=u.id, detalle="Registro público")
        return Response({"id": u.id, "nombre": u.first_name, "email": u.email, "rol": u.rol}, status=201)

@method_decorator(csrf_protect, name="dispatch")
class Login(APIView):
    permission_classes = []; authentication_classes = []; throttle_scope = "login"
    requerido = "usuario"
    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower(); password = request.data.get("password", "")
        u = authenticate(request, username=email, password=password)
        if not u or not u.is_active:
            registrar("sesion", "login_fallido", "denegado", referencia=email)
            return Response({"detail": "Correo o contraseña incorrectos"}, status=401)
        if u.rol != self.requerido:
            registrar("sesion", "login_fallido", "denegado", actor=u, referencia=email, detalle="Rol incorrecto")
            msg = "Esta entrada es para cuentas de usuario." if self.requerido == "usuario" else "Esta entrada es para cuentas administrativas."
            return Response({"detail": msg}, status=403)
        login(request, u); registrar("sesion", "login", "ok", actor=u)
        return Response({"id": u.id, "nombre": u.first_name, "email": u.email, "rol": u.rol})

class LoginAdmin(Login):
    requerido = "administrador"

@method_decorator(csrf_protect, name="dispatch")
class Logout(APIView):
    permission_classes = [EsUsuario | EsAdministrador]
    def post(self, request):
        registrar("sesion", "logout", "ok", actor=request.user); logout(request); return Response({"detail": "ok"})

class Me(APIView):
    permission_classes = [EsUsuario | EsAdministrador]
    def get(self, request): return Response({"id": request.user.id, "nombre": request.user.first_name, "email": request.user.email, "rol": request.user.rol})
