from types import SimpleNamespace
from django.test import SimpleTestCase
from analizador.reglas import evaluar_alerta


class AlertTests(SimpleTestCase):
    def test_intensidad_sostenida(self):
        self.assertTrue(
            evaluar_alerta(
                [SimpleNamespace(intensidad=8, categoria="ansiedad") for _ in range(3)]
            )["activa"]
        )

    def test_positive_and_ai_threshold(self):
        rs = [
            SimpleNamespace(
                intensidad=9,
                categoria="alegria",
                ia_patron_riesgo=False,
                ia_confianza=None,
            )
            for _ in range(4)
        ]
        self.assertFalse(evaluar_alerta(rs)["activa"])
        self.assertTrue(
            evaluar_alerta(
                [
                    SimpleNamespace(
                        intensidad=2,
                        categoria="calma",
                        ia_patron_riesgo=True,
                        ia_confianza=0.9,
                    )
                ]
            )["activa"]
        )
