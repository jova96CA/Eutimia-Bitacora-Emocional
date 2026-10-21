from django.core.management.base import BaseCommand
from getpass import getpass
from cuentas.models import Usuario

class Command(BaseCommand):
    help = "Crea una cuenta administradora"
    def handle(self, *args, **options):
        email = input("Correo: ").strip().lower(); nombre = input("Nombre: ").strip(); password = getpass("Contraseña: ")
        u = Usuario.objects.create_user(username=email, email=email, first_name=nombre, password=password, rol="administrador", is_staff=True)
        self.stdout.write(self.style.SUCCESS(f"Administrador creado: {u.email}"))
