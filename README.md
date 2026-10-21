# Bitácora de estado de ánimo

Aplicación académica para registrar estados de ánimo, consultar el historial y ver estadísticas personales. El análisis de texto es orientativo y nunca constituye un diagnóstico. Esta herramienta no sustituye atención profesional.

## Requisitos

- Python 3.10 o posterior.
- pip y un entorno virtual de Python.
- Windows PowerShell, macOS o Linux.

## Instalación y arranque

Desde la carpeta del proyecto:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# En macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
Copy-Item .env.example .env     # macOS/Linux: cp .env.example .env
python manage.py makemigrations cuentas emociones analizador auditoria
python manage.py migrate
python manage.py crear_admin
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` para el cliente y `http://127.0.0.1:8000/panel/` para la administración. El endpoint de salud CSRF está en `/api/v1/auth/csrf/`. El panel administrativo Django de desarrollo está en `/django-admin/`.

## Cuenta administradora

`python manage.py crear_admin` solicita correo, nombre y contraseña sin mostrarla al escribir. También se puede usar `python manage.py createsuperuser`; las cuentas superusuario reciben automáticamente el rol `administrador`.

El registro público crea siempre cuentas `usuario`; solo una cuenta administradora puede asignar ese rol desde la sección Usuarios.

## Configuración

Duplica `backend/.env.example` como `backend/.env`. Variables disponibles:

| Variable | Uso |
|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django; reemplázala localmente. |
| `DJANGO_DEBUG` | Activa el servidor de desarrollo y el servicio local de interfaces. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma. |
| `PROVEEDOR_IA` | `desactivado`, `simulado` u `openai`. |
| `OPENAI_API_KEY` | Clave opcional, solo para el proveedor OpenAI. |
| `IA_MODELO` | Modelo opcional para OpenAI. |
| `IA_TIMEOUT_SEGUNDOS` | Tiempo máximo de espera de IA. |

El modo `simulado` permite recorrer el flujo sin enviar texto a un servicio externo. Ninguna clave se guarda en el frontend ni en el repositorio. En modo OpenAI se envía solamente el texto libre.

## URLs principales

- Cliente: `/`
- Panel administrativo: `/panel/`
- API: `/api/v1/`
- Autenticación: `/api/v1/auth/`
- Registros personales: `/api/v1/registros/`
- Intérprete demostrativo: `/api/v1/interprete/analizar/`
- Auditoría y monitoreo (administrador): `/api/v1/admin/`

Las sesiones usan una sola cookie por navegador. Por eso, una cuenta de usuario y una administradora no pueden permanecer autenticadas simultáneamente en el mismo navegador; cerrar sesión en una interfaz cierra la sesión compartida.

## Pruebas

Desde `backend/`, ejecuta:

```powershell
python manage.py test
```

Las pruebas cubren el intérprete, cuentas y roles, privacidad, registros, estadísticas, alertas, proveedor de IA y endpoints administrativos.

## Seguridad y privacidad

- Cada historial y estadística consulta solo los registros del usuario autenticado.
- El administrador no tiene acceso a diarios ni a campos de registros; el monitor muestra conteos y metadatos técnicos.
- Los logs de análisis y auditoría no almacenan el texto libre, contraseñas, claves, cookies ni tokens completos.
- Si el análisis de IA falla, se conserva el registro y no se activa una alerta basada en IA.
- Los datos del navegador se pintan con `textContent`.
- Los endpoints de autenticación exigen CSRF y login/registro tienen límites de frecuencia.

Lista de revisión: [x] modelo de usuario configurado antes de migraciones · [x] rol público ignorado · [x] logins separados por rol · [x] CSRF en operaciones de sesión · [x] aislamiento por propietario y 404 para ids ajenos · [x] acceso de administrador bloqueado a datos personales · [x] validadores de contraseña · [x] logs sin texto libre · [x] throttling · [x] secretos solo en `.env` · [x] validación de salida de IA · [x] `textContent` en las interfaces.

## Decisiones

- Se mantuvo SQLite para la instalación local más simple; PostgreSQL queda como alternativa futura.
- Django sirve ambas interfaces en desarrollo para mantener el mismo origen y usar sesiones y CSRF nativos.
- El análisis simulado usa palabras clave deterministas y se mantiene como opción inicial sin credenciales.
- El mini-lenguaje acepta las categorías sin distinguir mayúsculas ni acentos y normaliza la categoría al guardar.
- Los recursos de apoyo se guardan en `backend/emociones/recursos_apoyo.py`. Los teléfonos deben confirmarse en canales oficiales antes de usar esta versión con personas reales.

## Pendientes

- Confirmar los teléfonos de apoyo mediante sus canales oficiales antes de cualquier uso con personas reales.
- No incluye despliegue de producción, recuperación de contraseña por correo, exportación, aplicación móvil ni interfaces con framework JavaScript.
