from django.test import TestCase, override_settings
from unittest.mock import patch
from types import SimpleNamespace
from django.contrib.auth import get_user_model
from analizador.ai_service import clasificar
from analizador.models import SolicitudIA
from analizador.pipeline import procesar_registro
from django.utils import timezone

U = get_user_model()


class AITests(TestCase):
    def test_simulated(self):
        u = U.objects.create_user(username="a", email="a@x", password="p")
        with override_settings(PROVEEDOR_IA="simulado"):
            r = clasificar(u, "No pude dormir")
            self.assertEqual(r["etiqueta_sentimiento"], "negativo")
        self.assertEqual(SolicitudIA.objects.get().estado, "completada")

    def test_invalid_json_fails_closed(self):
        u = U.objects.create_user(username="b", email="b@x", password="p")
        fake = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kw: SimpleNamespace(
                        choices=[
                            SimpleNamespace(message=SimpleNamespace(content="not json"))
                        ]
                    )
                )
            )
        )
        fake_module = SimpleNamespace(OpenAI=lambda **kw: fake)
        with override_settings(PROVEEDOR_IA="openai"), patch.dict(
            "sys.modules", {"openai": fake_module}
        ):
            self.assertIsNone(clasificar(u, "texto privado"))
        solicitud = SolicitudIA.objects.get()
        self.assertEqual(solicitud.estado, "fallida")
        self.assertEqual(solicitud.error_tipo, "formato")

    def test_disabled_provider_records_failure(self):
        u = U.objects.create_user(username="c", email="c@x", password="p")
        with override_settings(PROVEEDOR_IA="desactivado"):
            self.assertIsNone(clasificar(u, "texto"))
        solicitud = SolicitudIA.objects.get()
        self.assertEqual(solicitud.estado, "fallida")
        self.assertEqual(solicitud.error_tipo, "desactivada")

    def test_invalid_ai_does_not_block_saved_record(self):
        u = U.objects.create_user(username="d", email="d@x", password="p")
        fake = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kw: SimpleNamespace(
                        choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
                    )
                )
            )
        )
        with override_settings(PROVEEDOR_IA="openai"), patch.dict(
            "sys.modules", {"openai": SimpleNamespace(OpenAI=lambda **kw: fake)}
        ):
            r = procesar_registro(
                u,
                {
                    "fecha": timezone.localdate().isoformat(),
                    "intensidad": 9,
                    "categoria": "ansiedad",
                    "texto_libre": "texto",
                },
            )
        self.assertEqual(r.status, 201)
        self.assertFalse(r.cuerpo["alerta"]["activa"])
        self.assertFalse(r.cuerpo["analisis_texto"]["disponible"])
        self.assertEqual(SolicitudIA.objects.get().estado, "fallida")
