from django.test import TestCase, Client
from django.contrib.auth import get_user_model

U = get_user_model()


class MonitorTests(TestCase):
    def test_admin_only(self):
        c = Client()
        self.assertEqual(c.get("/api/v1/admin/monitor/ia/").status_code, 403)
        u = U.objects.create_user(
            username="a", email="a@x", password="p", rol="administrador"
        )
        c.force_login(u)
        self.assertEqual(c.get("/api/v1/admin/monitor/ia/").status_code, 200)
