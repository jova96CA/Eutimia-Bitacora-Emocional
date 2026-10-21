from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from analizador.pipeline import procesar_registro
from analizador.models import AnalisisLog, SolicitudIA
from auditoria.models import EventoAuditoria
from django.utils import timezone
U=get_user_model()
class PrivacyTests(TestCase):
 def test_text_not_logged(self):
  u=U.objects.create_user(username='a',email='a@x',password='p')
  with override_settings(PROVEEDOR_IA='simulado'):
   procesar_registro(u,{"fecha":timezone.localdate().isoformat(),"intensidad":5,"categoria":"calma","texto_libre":"SECRETO-12345"})
  for obj in list(AnalisisLog.objects.all())+list(SolicitudIA.objects.all())+list(EventoAuditoria.objects.all()):
   self.assertNotIn('SECRETO-12345',str(obj.__dict__))
