from datetime import timedelta
from collections import Counter
from django.utils import timezone
from .models import Registro
from analizador.reglas import calcular_tendencia

def racha_y_semana(registros, hoy=None):
    hoy = hoy or timezone.localdate(); fechas = set(registros.values_list("fecha", flat=True))
    actual = hoy; racha = 0
    if actual not in fechas: actual -= timedelta(days=1)
    while actual in fechas: racha += 1; actual -= timedelta(days=1)
    lunes = hoy - timedelta(days=hoy.weekday())
    return racha, [lunes + timedelta(days=i) in fechas for i in range(7)]

def construir_estadisticas(registros, dias, hoy=None):
    hoy = hoy or timezone.localdate(); desde = hoy - timedelta(days=dias-1)
    periodo = list(registros.filter(fecha__range=(desde, hoy)).order_by("fecha"))
    todos = list(registros)
    serie_map = {r.fecha: r.intensidad for r in periodo}
    serie = [{"fecha": (desde + timedelta(days=i)).isoformat(), "intensidad": serie_map.get(desde + timedelta(days=i))} for i in range(dias)]
    cats = Counter(r.categoria for r in todos)
    mes = sum(1 for r in todos if r.fecha.year == hoy.year and r.fecha.month == hoy.month)
    return {"dias": dias, "intensidad_promedio": round(sum(r.intensidad for r in periodo)/len(periodo), 1) if periodo else None, "categoria_frecuente": cats.most_common(1)[0][0] if cats else None, "dias_registrados_mes": mes, "serie": serie, "tendencia": calcular_tendencia(periodo)}
