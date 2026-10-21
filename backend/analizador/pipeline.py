from collections import Counter
from datetime import date
from django.utils import timezone
from django.db import IntegrityError
from rest_framework import status
from emociones.models import Registro
from emociones.serializers import RegistroSerializer
from analizador.interprete import interpretar
from analizador.models import AnalisisLog
from analizador.reglas import evaluar_alerta, detectar_urgencia
from analizador.mensajes import MENSAJES

class Resultado:
    def __init__(self, cuerpo, status_code): self.cuerpo, self.status = cuerpo, status_code

def procesar_registro(usuario, datos, hoy=None, actualizar=None):
    s = RegistroSerializer(data=datos)
    if not s.is_valid(): return Resultado({"detail": "El registro no es válido", "errores": s.errors}, 400)
    v = s.validated_data
    texto = v.get("texto_libre", "")
    copia = texto.replace('"', "'").replace("\n", " ").replace("\r", " ")
    linea = f'{v["fecha"]} {v["intensidad"]} {v["categoria"]}' + (f' "{copia}"' if texto else "")
    resultado = interpretar(linea, hoy or timezone.localdate())
    conteo = Counter(t.tipo for t in resultado["tokens"])
    estructura = {k: "ok" for k in ["fecha", "intensidad", "categoria", "texto"]}
    for e in resultado["errores"]: estructura[e.campo] = "error"
    AnalisisLog.objects.create(usuario=usuario, valido=resultado["valido"], num_tokens=len(resultado["tokens"]), tipos_token=dict(conteo), estructura=estructura, codigos_error=[e.codigo for e in resultado["errores"]])
    if not resultado["valido"]: return Resultado({"detail": "El registro no es válido", "errores": [e.__dict__ for e in resultado["errores"]]}, 400)
    reg_ast = resultado["registro"]
    if not actualizar and Registro.objects.filter(usuario=usuario, fecha=reg_ast.fecha).exists(): return Resultado({"detail": "Ya existe un registro para esta fecha"}, 409)
    try:
        if actualizar:
            for attr in ("fecha", "intensidad", "categoria", "texto_libre"): setattr(actualizar, attr, getattr(reg_ast, "texto", "") if attr == "texto_libre" else getattr(reg_ast, attr))
            registro = actualizar
        else:
            registro = Registro(usuario=usuario, fecha=reg_ast.fecha, intensidad=reg_ast.intensidad, categoria=reg_ast.categoria, texto_libre=texto)
        registro.save()
    except IntegrityError: return Resultado({"detail": "Ya existe un registro para esta fecha"}, 409)
    analisis = {"disponible": False, "mensaje": MENSAJES["no_disponible"]}
    if texto:
        from .ai_service import clasificar
        ai = clasificar(usuario, texto)
        if ai:
            registro.ia_etiqueta = ai["etiqueta_sentimiento"]; registro.ia_confianza = ai["confianza"]; registro.ia_patron_riesgo = ai["patron_riesgo"]; registro.save(update_fields=["ia_etiqueta", "ia_confianza", "ia_patron_riesgo"])
            analisis = {"disponible": True, "mensaje": MENSAJES[ai["etiqueta_sentimiento"]]}
    recientes = list(Registro.objects.filter(usuario=usuario).order_by("-fecha")[:4])
    alerta = {"activa": evaluar_alerta(recientes)["activa"]}
    return Resultado({"registro": RegistroSerializer(registro).data, "alerta": alerta, "urgente": detectar_urgencia(texto), "analisis_texto": analisis, "aviso": "Este análisis es orientativo y no sustituye la valoración de un profesional."}, 201 if not actualizar else 200)
