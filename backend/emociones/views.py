from datetime import date
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cuentas.permissions import EsUsuario
from .models import Registro
from .serializers import RegistroSerializer
from .estadisticas import construir_estadisticas, racha_y_semana
from .recursos_apoyo import RECURSOS_APOYO
from analizador.pipeline import procesar_registro
from analizador.reglas import evaluar_alerta


class RegistroListaCrear(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        qs = Registro.objects.filter(usuario=request.user)
        desde, hasta = request.query_params.get("desde"), request.query_params.get(
            "hasta"
        )
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)
        from rest_framework.pagination import PageNumberPagination

        p = PageNumberPagination()
        p.page_size = 30
        page = p.paginate_queryset(qs, request, view=self)
        return p.get_paginated_response(RegistroSerializer(page, many=True).data)

    def post(self, request):
        r = procesar_registro(request.user, request.data)
        return Response(r.cuerpo, status=r.status)


class RegistroDetalle(APIView):
    permission_classes = [EsUsuario]

    def get_obj(self, request, pk):
        return get_object_or_404(Registro, pk=pk, usuario=request.user)

    def get(self, request, pk):
        return Response(RegistroSerializer(self.get_obj(request, pk)).data)

    def put(self, request, pk):
        r = procesar_registro(
            request.user, request.data, actualizar=self.get_obj(request, pk)
        )
        return Response(r.cuerpo, status=r.status)

    def delete(self, request, pk):
        self.get_obj(request, pk).delete()
        return Response(status=204)


class Estadisticas(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        try:
            dias = int(request.query_params.get("dias", 7))
        except ValueError:
            return Response({"detail": "dias debe ser 7 o 30"}, status=400)
        if dias not in (7, 30):
            return Response({"detail": "dias debe ser 7 o 30"}, status=400)
        return Response(
            construir_estadisticas(Registro.objects.filter(usuario=request.user), dias)
        )


class Racha(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        r, semana = racha_y_semana(Registro.objects.filter(usuario=request.user))
        return Response({"racha": r, "semana": semana})


class Alerta(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        return Response(
            {
                "activa": evaluar_alerta(
                    Registro.objects.filter(usuario=request.user).order_by("-fecha")[:4]
                )["activa"]
            }
        )


class Recursos(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        return Response(RECURSOS_APOYO)
