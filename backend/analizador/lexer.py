import re
from dataclasses import dataclass

TOKEN_SPEC = [
    ("FECHA", r"\d{4}-\d{2}-\d{2}"),
    ("NUMERO", r"\d+"),
    ("TEXTO", r'"[^"\n]*"'),
    ("PALABRA", r"[^\W\d_]+"),
    ("ESPACIO", r"[ \t]+"),
    ("ERROR", r"."),
]
_MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))


@dataclass
class Token:
    tipo: str
    valor: str
    pos: int


@dataclass
class Error:
    codigo: str
    campo: str
    mensaje: str


def tokenizar(linea):
    tokens, errores = [], []
    for m in _MASTER.finditer(linea):
        tipo = m.lastgroup
        if tipo == "ESPACIO":
            continue
        if tipo == "ERROR":
            errores.append(
                Error(
                    "LEX_CARACTER_INVALIDO",
                    "linea",
                    f"Carácter no permitido en posición {m.start()}",
                )
            )
            continue
        tokens.append(Token(tipo, m.group(), m.start()))
    return tokens, errores
