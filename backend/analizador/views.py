from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from cuentas.permissions import EsUsuario
from cuentas.permissions import EsAdministrador
from .interprete import interpretar
from .models import AnalisisLog

class AnalizarLinea(APIView):
    permission_classes = [EsUsuario]
    def post(self, request):
        r = interpretar(request.data.get("linea", ""))
        return Response({"valido": r["valido"], "tokens": [t.__dict__ for t in r["tokens"]], "arbol": {"registro": r["registro"].__dict__} if r["registro"] else None, "errores": [e.__dict__ for e in r["errores"]]})

class MonitorAnalizador(APIView):
    permission_classes = [EsAdministrador]
    def get(self, request):
        data = AnalisisLog.objects.order_by("-creado_en")[:50]
        return Response([{"creado_en": x.creado_en, "valido": x.valido, "num_tokens": x.num_tokens, "tipos_token": x.tipos_token, "estructura": x.estructura, "codigos_error": x.codigos_error} for x in data])
