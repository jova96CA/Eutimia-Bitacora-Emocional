from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.management import call_command
from io import StringIO

U = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.c = Client(enforce_csrf_checks=True)

    def csrf(self):
        self.c.get("/api/v1/auth/csrf/")
        return self.c.cookies["csrftoken"].value

    def test_public_role_ignored(self):
        r = self.c.post(
            "/api/v1/auth/registro/",
            data='{"nombre":"Ana","email":"a@example.com","password":"Str0ng!Password-2026","password2":"Str0ng!Password-2026","rol":"administrador"}',
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.csrf(),
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(U.objects.get(email="a@example.com").rol, "usuario")

    def test_csrf_required(self):
        self.assertEqual(
            self.c.post(
                "/api/v1/auth/registro/", data="{}", content_type="application/json"
            ).status_code,
            403,
        )

    def test_login_role_boundaries(self):
        u = U.objects.create_user(
            username="u@e.com", email="u@e.com", password="StrongPass123!"
        )
        U.objects.create_user(
            username="a@e.com",
            email="a@e.com",
            password="StrongPass123!",
            rol="administrador",
        )
        self.c.get("/api/v1/auth/csrf/")
        token = self.c.cookies["csrftoken"].value
        self.assertEqual(
            self.c.post(
                "/api/v1/admin/auth/login/",
                data='{"email":"u@e.com","password":"StrongPass123!"}',
                content_type="application/json",
                HTTP_X_CSRFTOKEN=token,
            ).status_code,
            403,
        )
        self.c.logout()
        self.c.get("/api/v1/auth/csrf/")
        token = self.c.cookies["csrftoken"].value
        self.assertEqual(
            self.c.post(
                "/api/v1/auth/login/",
                data='{"email":"a@e.com","password":"StrongPass123!"}',
                content_type="application/json",
                HTTP_X_CSRFTOKEN=token,
            ).status_code,
            403,
        )

    def test_me_requires_session(self):
        self.assertIn(self.c.get("/api/v1/auth/me/").status_code, (401, 403))

    def test_superuser_role(self):
        u = U.objects.create_superuser(
            username="root@e.com", email="root@e.com", password="StrongPass123!"
        )
        self.assertEqual(u.rol, "administrador")
