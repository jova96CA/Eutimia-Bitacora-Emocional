import unicodedata
from datetime import date
from .lexer import Error

CATEGORIAS = {"ansiedad", "tristeza", "estres", "calma", "alegria"}
TEXTO_MAX = 200


def normalizar(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def validar(reg, hoy=None):
    hoy = hoy or date.today()
    errores = []
    try:
        if date.fromisoformat(reg.fecha) > hoy:
            errores.append(
                Error("SEM_FECHA_FUTURA", "fecha", "La fecha no puede ser futura")
            )
    except ValueError:
        errores.append(Error("SEM_FECHA_INVALIDA", "fecha", "Fecha inexistente"))
    if not 1 <= reg.intensidad <= 10:
        errores.append(
            Error(
                "SEM_INTENSIDAD_RANGO",
                "intensidad",
                "La intensidad debe estar entre 1 y 10",
            )
        )
    cat = normalizar(reg.categoria)
    if cat not in CATEGORIAS:
        errores.append(
            Error("SEM_CATEGORIA_INVALIDA", "categoria", "Categoría no reconocida")
        )
    else:
        reg.categoria = cat
    if len(reg.texto) > TEXTO_MAX:
        errores.append(Error("SEM_TEXTO_LARGO", "texto", "Máximo 200 caracteres"))
    return errores
