from .lexer import tokenizar
from .parser import parsear
from .semantic import validar


def interpretar(linea, hoy=None):
    tokens, e1 = tokenizar(linea)
    if e1:
        return {"valido": False, "tokens": tokens, "registro": None, "errores": e1}
    reg, e2 = parsear(tokens)
    if e2:
        return {"valido": False, "tokens": tokens, "registro": None, "errores": e2}
    e3 = validar(reg, hoy)
    return {
        "valido": not e3,
        "tokens": tokens,
        "registro": reg if not e3 else None,
        "errores": e3,
    }
