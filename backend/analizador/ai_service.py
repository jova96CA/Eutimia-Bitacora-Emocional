import json
import time
from django.conf import settings
from .models import SolicitudIA


def _validar(data):
    return (
        isinstance(data, dict)
        and data.get("etiqueta_sentimiento") in {"positivo", "neutro", "negativo"}
        and isinstance(data.get("confianza"), (int, float))
        and 0 <= data["confianza"] <= 1
        and isinstance(data.get("patron_riesgo"), bool)
        and isinstance(data.get("explicacion_breve"), str)
        and len(data["explicacion_breve"]) <= 200
    )


def clasificar(usuario, texto):
    inicio = time.monotonic()
    resultado = None
    error = ""
    try:
        proveedor = settings.PROVEEDOR_IA
        if proveedor == "simulado":
            bajo = texto.lower()
            etiqueta = (
                "negativo"
                if any(
                    p in bajo
                    for p in [
                        "no pude dormir",
                        "agobiado",
                        "triste",
                        "ansiedad",
                        "estres",
                        "estrés",
                    ]
                )
                else (
                    "positivo"
                    if any(p in bajo for p in ["feliz", "bien", "alegre", "contento"])
                    else "neutro"
                )
            )
            resultado = {
                "etiqueta_sentimiento": etiqueta,
                "confianza": 0.8,
                "patron_riesgo": False,
                "explicacion_breve": "Análisis simulado",
            }
        elif proveedor == "openai":
            from openai import OpenAI

            client = OpenAI(
                api_key=settings.OPENAI_API_KEY, timeout=settings.IA_TIMEOUT_SEGUNDOS
            )
            response = client.chat.completions.create(
                model=settings.IA_MODELO,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Clasifica sentimiento de forma orientativa, no diagnostiques. "
                            "Devuelve solo JSON con etiqueta_sentimiento, confianza, "
                            "patron_riesgo y explicacion_breve."
                        ),
                    },
                    {"role": "user", "content": texto},
                ],
            )
            resultado = json.loads(response.choices[0].message.content or "")
        else:
            error = "desactivada"
        if resultado is not None and not _validar(resultado):
            resultado = None
            error = "formato"
    except json.JSONDecodeError:
        resultado = None
        error = "formato"
    except Exception as exc:
        resultado = None
        error = "timeout" if "timeout" in type(exc).__name__.lower() else "red"
    ms = int((time.monotonic() - inicio) * 1000)
    SolicitudIA.objects.create(
        usuario=usuario,
        estado="completada" if resultado else "fallida",
        tiempo_ms=ms,
        esquema_valido=bool(resultado) if error != "desactivada" else None,
        error_tipo=error,
    )
    return resultado
