import unicodedata
VENTANA_REGISTROS = 4
INTENSIDAD_ALTA = 8
MIN_REGISTROS_ALTOS = 3
CATEGORIAS_DIFICILES = {"ansiedad", "tristeza", "estres"}
CATEGORIAS_POSITIVAS = {"calma", "alegria"}
UMBRAL_CONFIANZA_IA = 0.75
UMBRAL_TENDENCIA = 2
PALABRAS_URGENCIA = ["quiero morir", "no quiero vivir", "quitarme la vida", "hacerme dano", "suicid"]
def _normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
def evaluar_alerta(registros_recientes):
    recientes = list(registros_recientes)[:VENTANA_REGISTROS]
    altos = sum(r.intensidad >= INTENSIDAD_ALTA and r.categoria in CATEGORIAS_DIFICILES for r in recientes)
    if altos >= MIN_REGISTROS_ALTOS: return {"activa": True, "motivo": "intensidad_sostenida"}
    if recientes:
        r = recientes[0]
        if r.ia_patron_riesgo and (r.ia_confianza or 0) >= UMBRAL_CONFIANZA_IA: return {"activa": True, "motivo": "senal_ia"}
    return {"activa": False, "motivo": None}
def detectar_urgencia(texto): return any(p in _normalizar(texto) for p in PALABRAS_URGENCIA)
def calcular_tendencia(registros):
    vals = [(r.intensidad if r.categoria in CATEGORIAS_POSITIVAS else -r.intensidad) for r in registros]
    promedio = sum(vals) / len(vals) if vals else 0
    return "positiva" if promedio >= UMBRAL_TENDENCIA else "negativa" if promedio <= -UMBRAL_TENDENCIA else "neutral"
