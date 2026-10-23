from rest_framework.views import APIView
from rest_framework.response import Response
from cuentas.permissions import EsAdministrador
from .models import EventoAuditoria
from analizador.models import SolicitudIA
from django.db.models import Avg


class Auditoria(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        qs = EventoAuditoria.objects.order_by("-creado_en")
        cat = request.query_params.get("categoria")
        if cat in ("admin", "sesion"):
            qs = qs.filter(categoria=cat)
        desde = request.query_params.get("desde")
        if desde:
            qs = qs.filter(creado_en__date__gte=desde)
        return Response(
            [
                {
                    "creado_en": e.creado_en,
                    "categoria": e.categoria,
                    "accion": e.accion,
                    "resultado": e.resultado,
                    "actor": e.actor.email if e.actor else None,
                    "objetivo_id": e.objetivo_id,
                    "referencia": e.referencia,
                    "detalle": e.detalle,
                }
                for e in qs[:100]
            ]
        )


class MonitorIA(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        qs = SolicitudIA.objects.order_by("-creado_en")
        return Response(
            {
                "resumen": {
                    "total": qs.count(),
                    "fallidas": qs.filter(estado="fallida").count(),
                    "tiempo_promedio_ms": qs.aggregate(x=Avg("tiempo_ms"))["x"],
                },
                "solicitudes": [
                    {
                        "creado_en": x.creado_en,
                        "estado": x.estado,
                        "tiempo_ms": x.tiempo_ms,
                        "esquema_valido": x.esquema_valido,
                        "error_tipo": x.error_tipo,
                    }
                    for x in qs[:50]
                ],
            }
        )
