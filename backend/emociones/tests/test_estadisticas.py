from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from emociones.models import Registro
from emociones.estadisticas import construir_estadisticas, racha_y_semana
U=get_user_model()
class StatsTests(TestCase):
 def test_stats_and_streak(self):
  u=U.objects.create_user(username='a@x',email='a@x',password='p'); hoy=timezone.localdate()
  for i in range(3): Registro.objects.create(usuario=u,fecha=hoy-timedelta(days=i),intensidad=9,categoria='alegria')
  d=construir_estadisticas(Registro.objects.filter(usuario=u),7,hoy); self.assertEqual(d['intensidad_promedio'],9); self.assertEqual(d['categoria_frecuente'],'alegria'); self.assertTrue(any(x['intensidad'] is None for x in d['serie'])); self.assertEqual(d['tendencia'],'positiva')
  self.assertEqual(racha_y_semana(Registro.objects.filter(usuario=u),hoy)[0],3)
