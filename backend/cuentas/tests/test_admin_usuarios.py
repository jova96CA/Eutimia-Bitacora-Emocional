from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from auditoria.models import EventoAuditoria

U = get_user_model()


class AdminUsersTests(TestCase):
    def test_permissions_and_audit(self):
        normal = U.objects.create_user(username="u", email="u@x", password="p")
        admin = U.objects.create_user(
            username="a", email="a@x", password="p", rol="administrador"
        )
        c = Client()
        c.force_login(normal)
        self.assertEqual(c.get("/api/v1/admin/usuarios/").status_code, 403)
        c.force_login(admin)
        r = c.post(
            f"/api/v1/admin/usuarios/{normal.id}/asignar-rol/",
            {"rol": "administrador"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(EventoAuditoria.objects.filter(accion="rol_asignado").exists())
