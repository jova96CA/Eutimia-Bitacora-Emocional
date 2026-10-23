from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from emociones.models import Registro
import json

U = get_user_model()


class RegistroTests(TestCase):
    def setUp(self):
        self.a = U.objects.create_user(
            username="a@e.com", email="a@e.com", password="pw"
        )
        self.b = U.objects.create_user(
            username="b@e.com", email="b@e.com", password="pw"
        )
        self.c = Client()
        self.c.force_login(self.a)

    def payload(self, **kw):
        return {
            "fecha": timezone.localdate().isoformat(),
            "intensidad": 5,
            "categoria": "ansiedad",
            "texto_libre": "",
            **kw,
        }

    def test_create_and_validation(self):
        self.assertEqual(
            self.c.post(
                "/api/v1/registros/", self.payload(), content_type="application/json"
            ).status_code,
            201,
        )
        self.assertEqual(
            self.c.post(
                "/api/v1/registros/", self.payload(), content_type="application/json"
            ).status_code,
            409,
        )

    def test_future_and_intensity(self):
        d = self.payload(fecha="2999-01-01")
        self.assertEqual(
            self.c.post(
                "/api/v1/registros/", d, content_type="application/json"
            ).status_code,
            400,
        )
        self.assertEqual(
            self.c.post(
                "/api/v1/registros/",
                self.payload(intensidad=11),
                content_type="application/json",
            ).status_code,
            400,
        )

    def test_other_user_hidden_and_admin_forbidden(self):
        r = Registro.objects.create(
            usuario=self.b, fecha=timezone.localdate(), intensidad=5, categoria="calma"
        )
        self.assertEqual(self.c.get(f"/api/v1/registros/{r.id}/").status_code, 404)
        admin = U.objects.create_user(
            username="x@e.com", email="x@e.com", password="pw", rol="administrador"
        )
        self.c.force_login(admin)
        self.assertEqual(self.c.get("/api/v1/registros/").status_code, 403)
