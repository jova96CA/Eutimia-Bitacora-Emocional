import unittest
from datetime import date
from analizador.interprete import interpretar

class InterpreteTests(unittest.TestCase):
    def codigo(self, linea, hoy=date(2026, 10, 12)):
        return [e.codigo for e in interpretar(linea, hoy)["errores"]]
    def test_valido_con_texto(self): self.assertTrue(interpretar('2026-10-12 8 Ansiedad "No dormí bien"', date(2026,10,12))["valido"])
    def test_valido_sin_texto(self): self.assertTrue(interpretar("2026-10-12 5 Estrés", date(2026,10,12))["valido"])
    def test_intensidad(self): self.assertIn("SEM_INTENSIDAD_RANGO", self.codigo("2026-10-12 11 Calma"))
    def test_categoria(self): self.assertIn("SEM_CATEGORIA_INVALIDA", self.codigo("2026-10-12 5 Enojo"))
    def test_futura(self): self.assertIn("SEM_FECHA_FUTURA", self.codigo("2026-10-13 5 Calma"))
    def test_fecha_imposible(self): self.assertIn("SEM_FECHA_INVALIDA", self.codigo("2026-02-31 5 Calma"))
    def test_palabra_faltante(self): self.assertIn("SINT_ESPERABA_PALABRA", self.codigo("2026-10-12 5"))
    def test_tokens_sobrantes(self): self.assertIn("SINT_TOKEN_SOBRANTE", self.codigo('2026-10-12 5 Calma "a" "b"'))
    def test_caracter_invalido(self): self.assertIn("LEX_CARACTER_INVALIDO", self.codigo("2026-10-12 5 Calma @"))
    def test_texto_largo(self): self.assertIn("SEM_TEXTO_LARGO", self.codigo('2026-10-12 5 Calma "' + "a"*201 + '"'))
