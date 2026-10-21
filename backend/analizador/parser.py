from dataclasses import dataclass
from .lexer import Error

@dataclass
class RegistroAST:
    fecha: str
    intensidad: int
    categoria: str
    texto: str = ""
def parsear(tokens):
    esperado = ["FECHA", "NUMERO", "PALABRA"]
    for i, tipo in enumerate(esperado):
        if i >= len(tokens) or tokens[i].tipo != tipo: return None, [Error("SINT_ESPERABA_" + tipo, tipo.lower(), f"Se esperaba {tipo}")]
    resto = tokens[3:]; texto = ""
    if resto:
        if resto[0].tipo != "TEXTO" or len(resto) > 1: return None, [Error("SINT_TOKEN_SOBRANTE", "texto", "Tokens inesperados al final del registro")]
        texto = resto[0].valor[1:-1]
    f, n, c = tokens[:3]
    return RegistroAST(f.valor, int(n.valor), c.valor, texto), []
