# AGENTS.md — Bitácora de estado de ánimo (versión básica)

Instrucciones para construir el proyecto **"Bitácora de estado de ánimo para la detección de trastornos emocionales"**. Proyecto académico (Lenguajes y Autómatas, ISC, Instituto Tecnológico de Tijuana). Lee este archivo completo antes de escribir código.

---

## 0. Cómo trabajar con este archivo

1. Trabaja **por fases** (sección 15). No pases a la siguiente fase hasta cumplir su "Hecho cuando".
2. Al terminar cada fase: ejecuta `python manage.py test` (desde `backend/`), corrige lo que falle y resume en 5 líneas qué se hizo y qué falta.
3. Haz lo **básico y funcional**. No agregues librerías, capas ni funciones que este archivo no pida.
4. Si algo es ambiguo, elige la opción más simple, déjala anotada en `README.md` (sección "Decisiones") y sigue.
5. Nombres de dominio en español (`registro`, `intensidad`, `categoria`, `usuario`), igual que en el resto del proyecto.

---

## 1. Objetivo y alcance

Aplicación web para registrar el estado de ánimo, consultar historial y estadísticas personales, y analizar de forma asistida el texto libre. Se compone de **tres piezas independientes**:

| Pieza | Carpeta | Qué es |
|---|---|---|
| API | `backend/` | Django + Django REST Framework. **Única** fuente de datos y de lógica. |
| Interfaz del cliente (usuario) | `frontend_cliente/` | HTML + CSS + JS puro. Solo habla con la API. |
| Interfaz administrativa | `frontend_admin/` | HTML + CSS + JS puro. Solo habla con la API. **Separada** de la del cliente. |

**Incluido en esta versión:** cuentas con roles (usuario / administrador), registro diario, historial, estadísticas, racha, intérprete del mini-lenguaje (lexer, parser, semántica), regla de alerta, análisis de texto con IA (con modo simulado), panel de administración con monitoreo y auditoría, pruebas.

**Fuera de alcance (no hacer):** app móvil, recuperación de contraseña por correo, notificaciones, exportación de datos, despliegue en producción, frameworks de frontend (React/Vue), paso de compilación (webpack/vite).

---

## 2. Reglas no negociables

1. **Nunca diagnosticar.** Ningún texto de la interfaz ni de la API afirma que una persona "tiene" un trastorno. El análisis es orientativo. Prohibido mostrar etiquetas como "riesgo alto" o "trastorno" al usuario.
2. **El administrador no lee diarios.** No existe ningún endpoint que devuelva `texto_libre`, `intensidad` ni `categoria` de otros usuarios. Un administrador que llame a `/registros/` recibe 403.
3. **El rol administrador jamás se asigna desde el registro público.** El campo `rol` se ignora en cualquier endpoint público.
4. **Sin secretos en el repositorio.** Claves y configuración sensible solo en `.env` (que está en `.gitignore`). Se entrega `.env.example`.
5. **Los logs técnicos no contienen contenido emocional**: ni `texto_libre`, ni contraseñas, ni claves, ni tokens completos, ni cookies.
6. **Si la IA falla, no hay alerta por IA.** Ante timeout, error o respuesta inválida: el registro se guarda igual, se anota la solicitud como fallida y se asume "sin patrón de riesgo". Nunca al revés.
7. **Aviso permanente** en ambas interfaces: "Esta herramienta no sustituye atención profesional."
8. **Tokens de sesión ≠ tokens lingüísticos.** En el panel admin se muestran en secciones distintas y no se mezclan los nombres (`sesion` vs `token_lexico`).

---

## 3. Arquitectura

```
 Navegador (usuario)               Navegador (administrador)
 frontend_cliente/                 frontend_admin/
 HTML+CSS+JS (fetch)               HTML+CSS+JS (fetch)
           \                               /
            \        /api/v1/... (JSON)   /
             v                           v
        ┌───────────────────────────────────────┐
        │ backend/  Django + DRF                │
        │ cuentas · emociones · analizador ·    │
        │ auditoria                             │
        └──────────────────┬────────────────────┘
                           │
              SQLite (dev) / PostgreSQL
                           │ (opcional, solo texto libre)
                     API de IA externa
```

**Decisión: mismo origen + sesiones de Django.** En desarrollo, Django sirve las dos interfaces y la API desde `http://127.0.0.1:8000`:

| URL | Qué sirve |
|---|---|
| `/` | `frontend_cliente/` |
| `/panel/` | `frontend_admin/` |
| `/api/v1/` | API REST |
| `/django-admin/` | Admin nativo de Django (solo superusuario, solo para desarrollo; **no** es el panel del producto) |

Ventajas: sin CORS, cookies de sesión `HttpOnly`, CSRF nativo y es lo que recomienda el documento de diseño. Las dos interfaces siguen **separadas** (carpetas, páginas, login y permisos distintos); solo comparten el servidor.

Limitación conocida (documentarla en README): la sesión usa una sola cookie por navegador, así que un usuario y un administrador no pueden estar logueados a la vez en el mismo navegador. Cerrar sesión en uno cierra la del otro.

*Evolución futura (no hacer ahora):* si se separan los orígenes, agregar `django-cors-headers`, `CORS_ALLOW_CREDENTIALS=True`, `CSRF_TRUSTED_ORIGINS` y `SESSION_COOKIE_SAMESITE="None"` con HTTPS; o cambiar a JWT.

---

## 4. Estructura de carpetas

```
bitacora/
├── AGENTS.md
├── README.md
├── .gitignore
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py              # rutas raíz + servir frontends en DEBUG
│   │   ├── api_urls.py          # incluye las urls de cada app bajo /api/v1/
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── cuentas/
│   │   ├── models.py            # Usuario con rol
│   │   ├── serializers.py
│   │   ├── permissions.py       # EsUsuario, EsAdministrador
│   │   ├── views_auth.py        # csrf, registro, login, login admin, logout, me
│   │   ├── views_admin.py       # CRUD de cuentas (solo administrador)
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── management/commands/crear_admin.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_auth.py
│   │       └── test_admin_usuarios.py
│   ├── emociones/
│   │   ├── models.py            # Registro
│   │   ├── serializers.py
│   │   ├── views.py             # registros, estadisticas, racha, alerta, recursos
│   │   ├── estadisticas.py      # cálculos puros
│   │   ├── recursos_apoyo.py    # lista de recursos de apoyo
│   │   ├── urls.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_registros.py
│   │       ├── test_estadisticas.py
│   │       └── test_alerta.py
│   ├── analizador/
│   │   ├── models.py            # AnalisisLog, SolicitudIA
│   │   ├── lexer.py             # texto -> tokens
│   │   ├── parser.py            # tokens -> Registro (AST)
│   │   ├── semantic.py          # reglas de significado
│   │   ├── interprete.py        # orquesta lexer+parser+semantic
│   │   ├── reglas.py            # constantes: alerta, tendencia, urgencia
│   │   ├── mensajes.py          # frases prudentes para el usuario
│   │   ├── ai_service.py        # proveedor de IA (desactivado/simulado/openai)
│   │   ├── pipeline.py          # flujo completo de un registro
│   │   ├── urls.py              # /interprete/analizar/
│   │   ├── views.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_interprete.py     # Python puro, sin base de datos
│   │       ├── test_ai_service.py
│   │       └── test_privacidad_logs.py
│   └── auditoria/
│       ├── models.py            # EventoAuditoria
│       ├── servicios.py         # registrar(...)
│       ├── views.py             # auditoria + monitor (solo administrador)
│       ├── urls.py
│       └── tests/
│           ├── __init__.py
│           └── test_monitor.py
├── frontend_cliente/
│   ├── index.html               # redirige a app.html o login.html
│   ├── login.html
│   ├── registro.html            # crear cuenta
│   ├── app.html                 # pestañas: Registrar · Historial · Estadísticas
│   ├── css/estilos.css
│   └── js/
│       ├── api.js               # wrapper de fetch (CSRF, errores)
│       ├── auth.js              # login, registro, logout, guardia de sesión
│       ├── ui.js                # pestañas, avisos
│       ├── registrar.js         # formulario + racha
│       ├── historial.js
│       ├── estadisticas.js      # tarjetas + gráfica SVG
│       └── alerta.js            # banner y modal de recursos
└── frontend_admin/
    ├── index.html               # redirige a panel.html o login.html
    ├── login.html
    ├── panel.html               # barra lateral con 5 secciones
    ├── css/admin.css
    └── js/
        ├── api.js               # copia propia (no compartir archivos con el cliente)
        ├── auth.js
        ├── usuarios.js
        ├── monitor.js           # sesiones, analizador, IA
        └── auditoria.js
```

`.gitignore` mínimo: `.venv/`, `.env`, `db.sqlite3`, `__pycache__/`, `*.pyc`.

---

## 5. Arranque del proyecto

```bash
mkdir bitacora && cd bitacora
mkdir backend frontend_cliente frontend_admin
cd backend
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# Linux/macOS:         source .venv/bin/activate
```

`backend/requirements.txt`:

```
Django>=5.2,<5.3
djangorestframework>=3.15
python-dotenv>=1.0
# Solo si PROVEEDOR_IA=openai:
openai>=1.0
```

```bash
pip install -r requirements.txt
django-admin startproject config .
python manage.py startapp cuentas
python manage.py startapp emociones
python manage.py startapp analizador
python manage.py startapp auditoria
```

`backend/.env.example` (copiar a `.env`):

```
DJANGO_SECRET_KEY=cambia-esto-en-local
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
# Proveedor de IA: desactivado | simulado | openai
PROVEEDOR_IA=simulado
OPENAI_API_KEY=
IA_MODELO=
IA_TIMEOUT_SEGUNDOS=8
```

Puntos clave de `config/settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    # ...apps predeterminadas de Django...
    "rest_framework",
    "cuentas", "emociones", "analizador", "auditoria",
]

AUTH_USER_MODEL = "cuentas.Usuario"       # ANTES de la primera migración
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Tijuana"
USE_TZ = True

FRONTEND_CLIENTE_DIR = BASE_DIR.parent / "frontend_cliente"
FRONTEND_ADMIN_DIR = BASE_DIR.parent / "frontend_admin"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 30,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"login": "10/min", "registro": "10/hour"},
}

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
# En producción: SESSION_COOKIE_SECURE = True, CSRF_COOKIE_SECURE = True, SECURE_SSL_REDIRECT = True

PROVEEDOR_IA = os.environ.get("PROVEEDOR_IA", "desactivado")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
IA_MODELO = os.environ.get("IA_MODELO", "")
IA_TIMEOUT_SEGUNDOS = int(os.environ.get("IA_TIMEOUT_SEGUNDOS", "8"))
```

`config/urls.py` (las dos interfaces solo se sirven así en `DEBUG`; en producción las serviría el servidor web):

```python
from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve


def servir(raiz):
    def vista(request, path=""):
        return serve(request, path or "index.html", document_root=raiz)
    return vista


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/", include("config.api_urls")),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r"^panel/(?P<path>.*)$", servir(settings.FRONTEND_ADMIN_DIR)),
        re_path(r"^(?P<path>.*)$", servir(settings.FRONTEND_CLIENTE_DIR)),   # siempre al final
    ]
```

Primera ejecución:

```bash
python manage.py makemigrations cuentas emociones analizador auditoria
python manage.py migrate
python manage.py crear_admin          # pide correo y contraseña
python manage.py runserver
```

---

## 6. Cómo se crea la API (receta que se repite en cada recurso)

Para **cada** recurso sigue siempre este orden. Es el patrón de toda la API:

1. **Modelo** (`models.py`) — la tabla.
2. **Serializer** (`serializers.py`) — qué campos entran y salen, y sus validaciones de forma.
3. **Permiso** (`permissions.py`) — quién puede llamar (`EsUsuario` o `EsAdministrador`).
4. **Vista** (`views.py`) — usa `APIView` o `generics.*`; **siempre** filtra por `request.user` en los recursos personales.
5. **URL** (`urls.py` de la app) y se incluye en `config/api_urls.py`.
6. **Prueba** (`tests/`) — éxito, validación, sin sesión (401/403) y rol incorrecto (403).

`config/api_urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path("", include("cuentas.urls")),
    path("", include("emociones.urls")),
    path("", include("analizador.urls")),
    path("", include("auditoria.urls")),
]
```

`cuentas/permissions.py`:

```python
from rest_framework.permissions import BasePermission


class EsUsuario(BasePermission):
    """Solo cuentas activas con rol 'usuario'. El administrador queda fuera a propósito."""
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_active and u.rol == "usuario")


class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_active and u.rol == "administrador")
```

Ejemplo completo del patrón con `Registro` (fragmento de `emociones/views.py`):

```python
class RegistroListaCrear(APIView):
    permission_classes = [EsUsuario]

    def get(self, request):
        qs = Registro.objects.filter(usuario=request.user)      # SIEMPRE filtrar por dueño
        # filtros opcionales ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
        pagina = self.paginator.paginate_queryset(qs, request) ...
        return self.paginator.get_paginated_response(RegistroSerializer(pagina, many=True).data)

    def post(self, request):
        resultado = pipeline.procesar_registro(request.user, request.data)   # ver sección 9
        return Response(resultado.cuerpo, status=resultado.status)
```

CSRF en login/registro/logout: DRF solo exige CSRF a usuarios ya autenticados, así que estas tres vistas deben protegerse explícitamente:

```python
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

@method_decorator(csrf_protect, name="dispatch")
class LoginCliente(APIView):
    permission_classes = []
    authentication_classes = []
    throttle_scope = "login"
    ...

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfToken(APIView):
    permission_classes = []
    authentication_classes = []
    def get(self, request):
        return Response({"detail": "ok"})
```

Formato de error uniforme (400):

```json
{"detail": "El registro no es válido",
 "errores": [{"codigo": "SEM_INTENSIDAD_RANGO", "campo": "intensidad", "mensaje": "La intensidad debe estar entre 1 y 10"}]}
```

---

## 7. Modelos

### `cuentas.Usuario`

```python
class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        USUARIO = "usuario", "Usuario"
        ADMINISTRADOR = "administrador", "Administrador"

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.USUARIO)

    def save(self, *args, **kwargs):
        if self.is_superuser:               # createsuperuser debe producir un administrador real
            self.rol = self.Rol.ADMINISTRADOR
        super().save(*args, **kwargs)
```

- Se inicia sesión con **correo**: al registrar, `username = email.lower()`. `first_name` guarda el nombre.
- Comando `crear_admin` (en `cuentas/management/commands/`): pide correo, nombre y contraseña, crea usuario con `rol=administrador`, `is_staff=True`.

### `emociones.Registro`

```python
class Registro(models.Model):
    class Categoria(models.TextChoices):
        ANSIEDAD = "ansiedad", "Ansiedad"
        TRISTEZA = "tristeza", "Tristeza"
        ESTRES = "estres", "Estrés"
        CALMA = "calma", "Calma"
        ALEGRIA = "alegria", "Alegría"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registros")
    fecha = models.DateField()
    intensidad = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    texto_libre = models.CharField(max_length=200, blank=True)
    # Resumen acotado del análisis de IA (nunca la explicación completa):
    ia_etiqueta = models.CharField(max_length=10, blank=True)          # positivo|neutro|negativo
    ia_confianza = models.FloatField(null=True, blank=True)
    ia_patron_riesgo = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        constraints = [models.UniqueConstraint(fields=["usuario", "fecha"], name="un_registro_por_dia")]
```

Regla: **un registro por usuario por día**. Un segundo `POST` el mismo día responde 409; para cambiarlo se usa `PUT`.

### `analizador.AnalisisLog` (qué pasó en el intérprete, **sin texto**)

`creado_en`, `usuario` (FK, `SET_NULL`), `valido` (bool), `num_tokens` (int), `tipos_token` (JSON: `{"FECHA":1,"NUMERO":1,"PALABRA":1,"TEXTO":1}`), `estructura` (JSON: `{"fecha":"ok","intensidad":"ok","categoria":"error","texto":"ok"}`), `codigos_error` (JSON: lista de códigos).

### `analizador.SolicitudIA`

`creado_en`, `usuario` (FK, `SET_NULL`), `estado` (`pendiente|completada|fallida`), `tiempo_ms` (int, null), `esquema_valido` (bool, null), `error_tipo` (`timeout|formato|red|desactivada|""`).

### `auditoria.EventoAuditoria`

`creado_en`, `categoria` (`sesion|admin|sistema`), `accion` (ej. `login`, `login_fallido`, `logout`, `permiso_denegado`, `usuario_creado`, `usuario_desactivado`, `rol_asignado`, `usuario_eliminado`), `resultado` (`ok|denegado|fallo`), `actor` (FK a Usuario, `SET_NULL`, null), `objetivo_id` (int, null), `referencia` (CharField 50: usuario intentado en un login fallido, truncado), `detalle` (CharField 200: **nunca** contenido emocional).

`auditoria/servicios.py` expone `registrar(categoria, accion, resultado, actor=None, objetivo_id=None, referencia="", detalle="")`. Llámalo desde login/logout, permisos denegados y cada acción del administrador.

---

## 8. Endpoints (`/api/v1/`)

Todas las respuestas son JSON. Las listas de historial usan paginación DRF (`count`, `next`, `previous`, `results`).

### Autenticación (compartida)

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET | `/auth/csrf/` | público | Fija la cookie `csrftoken`. Llamar antes de cualquier POST. |
| POST | `/auth/registro/` | público | `{nombre, email, password, password2}`. Crea `rol=usuario` siempre; ignora `rol` si viene. Valida con `AUTH_PASSWORD_VALIDATORS`. |
| POST | `/auth/login/` | público | `{email, password}`. **Solo** acepta `rol=usuario`; si es administrador responde 403 "Esta entrada es para cuentas de usuario." |
| POST | `/admin/auth/login/` | público | Igual, pero **solo** `rol=administrador`. |
| POST | `/auth/logout/` | autenticado | Cierra sesión. |
| GET | `/auth/me/` | autenticado | `{id, nombre, email, rol}`. Cada interfaz lo usa como guardia. |

Login fallido o con rol incorrecto: mensaje genérico ("Correo o contraseña incorrectos") y evento `login_fallido` en auditoría.

### Cliente (`EsUsuario`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/registros/?desde=&hasta=` | Historial **propio**, más reciente primero. |
| POST | `/registros/` | Crea registro (pasa por el intérprete). 201 / 400 / 409. |
| GET, PUT, DELETE | `/registros/{id}/` | Solo si es del usuario; si no, **404** (no 403, para no revelar existencia). |
| GET | `/estadisticas/?dias=7` (o `30`) | Ver abajo. |
| GET | `/racha/` | `{racha: 4, semana: [true,true,true,true,false,false,false]}` (lunes a domingo de la semana actual). |
| GET | `/alerta/` | `{activa: true}`. |
| GET | `/recursos-apoyo/` | Lista de recursos. |
| POST | `/interprete/analizar/` | Demo: `{linea}` → `{valido, tokens, arbol, errores}` sin guardar nada. |

**`POST /registros/`**

```json
// request
{"fecha": "2026-10-12", "intensidad": 8, "categoria": "ansiedad", "texto_libre": "No dormí bien por el examen"}

// 201
{
  "registro": {"id": 41, "fecha": "2026-10-12", "intensidad": 8, "categoria": "ansiedad",
               "texto_libre": "No dormí bien por el examen", "creado_en": "2026-10-12T20:41:00-07:00"},
  "alerta": {"activa": true},
  "urgente": false,
  "analisis_texto": {"disponible": true, "mensaje": "Tu texto refleja un día pesado. Gracias por escribirlo."},
  "aviso": "Este análisis es orientativo y no sustituye la valoración de un profesional."
}
```

La respuesta **no** incluye `etiqueta`, `confianza` ni `patron_riesgo`; el cliente solo recibe el `mensaje` prudente (de `analizador/mensajes.py`). Si la IA no está disponible: `"analisis_texto": {"disponible": false, "mensaje": "Tu registro se guardó. El análisis del texto no estuvo disponible esta vez."}`. 409 si ya existe registro ese día.

**`GET /estadisticas/?dias=7`**

```json
{
  "dias": 7,
  "intensidad_promedio": 5.3,
  "categoria_frecuente": "calma",
  "dias_registrados_mes": 18,
  "serie": [{"fecha": "2026-10-06", "intensidad": 4}, {"fecha": "2026-10-07", "intensidad": null}],
  "tendencia": "neutral"
}
```

`tendencia` ∈ `positiva | neutral | negativa` (regla en `reglas.py`, sección 9.4). `serie` incluye **todos** los días del periodo, con `null` donde no hay registro. `categoria_frecuente` es `null` si no hay registros.

### Administrador (`EsAdministrador`)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/admin/usuarios/?q=&activo=` | Lista de cuentas: `id, nombre, email, rol, is_active, date_joined, num_registros` (solo el **conteo**). |
| POST | `/admin/usuarios/` | Crea cuenta con `rol=usuario`. |
| PATCH | `/admin/usuarios/{id}/` | Edita `nombre`, `email`, `is_active`. |
| DELETE | `/admin/usuarios/{id}/` | Elimina cuenta y sus registros (el frontend pide confirmación; se prefiere desactivar). |
| POST | `/admin/usuarios/{id}/asignar-rol/` | `{rol}`. Única vía para crear administradores. |
| GET | `/admin/auditoria/?categoria=sesion\|admin&desde=` | Eventos de auditoría (últimos 100). |
| GET | `/admin/monitor/analizador/` | Últimos 50 `AnalisisLog`. |
| GET | `/admin/monitor/ia/` | Últimas 50 `SolicitudIA` + resumen `{total, fallidas, tiempo_promedio_ms}`. |

Reglas de la API de administración:
- Un administrador **no puede** desactivarse, eliminarse ni quitarse el rol a sí mismo, ni dejar el sistema sin ningún administrador activo (400).
- Cada acción (`usuario_creado`, `usuario_desactivado`, `rol_asignado`, `usuario_eliminado`) genera un `EventoAuditoria` con `actor` y `objetivo_id`.
- No existe ningún endpoint de administración que devuelva contenido de registros.

---

## 9. Analizador (el intérprete — núcleo de la materia)

### 9.1 Gramática del mini-lenguaje

Un registro diario es una línea de texto:

```
<registro>    ::= <fecha> <intensidad> <categoria> [<texto_libre>]
<fecha>       ::= AAAA "-" MM "-" DD
<intensidad>  ::= entero de 1 a 10
<categoria>   ::= "Ansiedad" | "Tristeza" | "Estres" | "Calma" | "Alegria"     (sin distinguir mayúsculas ni acentos)
<texto_libre> ::= '"' cadena de hasta 200 caracteres sin comillas '"'
```

Ejemplo: `2026-10-12 8 Ansiedad "No dormí bien"`

La API **construye esta línea** a partir de los campos del formulario y la pasa por el intérprete; así el formulario y el mini-lenguaje son lo mismo. (Al construirla: reemplaza `"` por `'` y saltos de línea por espacio en una **copia**; el `texto_libre` original se guarda sin alterar.)

### 9.2 Fases y responsabilidad

| Fase | Archivo | Qué hace |
|---|---|---|
| Léxica | `lexer.py` | Expresiones regulares (equivalen a un autómata finito) → tokens `FECHA`, `NUMERO`, `TEXTO`, `PALABRA`. Carácter desconocido → `LEX_CARACTER_INVALIDO`. |
| Sintáctica | `parser.py` | Verifica `FECHA NUMERO PALABRA [TEXTO] fin` y construye el objeto `Registro` (AST simple). Errores `SINT_*`. |
| Semántica | `semantic.py` | Fecha real y no futura, intensidad 1–10, categoría del conjunto cerrado, texto ≤ 200. Errores `SEM_*`. |
| Orquestación | `interprete.py` | `interpretar(linea, hoy)` → `{valido, tokens, registro, errores}`. Sin dependencias de Django (Python puro, probable sin base de datos). |

Códigos de error: `LEX_CARACTER_INVALIDO`, `SINT_ESPERABA_FECHA`, `SINT_ESPERABA_NUMERO`, `SINT_ESPERABA_PALABRA`, `SINT_TOKEN_SOBRANTE`, `SEM_FECHA_INVALIDA`, `SEM_FECHA_FUTURA`, `SEM_INTENSIDAD_RANGO`, `SEM_CATEGORIA_INVALIDA`, `SEM_TEXTO_LARGO`.

### 9.3 Implementación de referencia (probada)

Esta versión ya se ejecutó contra 11 casos válidos e inválidos y produce los códigos indicados. Divídela en `lexer.py`, `parser.py`, `semantic.py` e `interprete.py` conservando el comportamiento. `hoy` debe pasarse como `timezone.localdate()` desde la API.

```python
import re
import unicodedata
from dataclasses import dataclass
from datetime import date

CATEGORIAS = {"ansiedad", "tristeza", "estres", "calma", "alegria"}
TEXTO_MAX = 200

TOKEN_SPEC = [
    ("FECHA", r"\d{4}-\d{2}-\d{2}"),     # antes que NUMERO
    ("NUMERO", r"\d+"),
    ("TEXTO", r'"[^"\n]*"'),
    ("PALABRA", r"[^\W\d_]+"),           # letras con acentos y ñ
    ("ESPACIO", r"[ \t]+"),
    ("ERROR", r"."),
]
_MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))


@dataclass
class Token:
    tipo: str
    valor: str
    pos: int


@dataclass
class Error:
    codigo: str
    campo: str
    mensaje: str


@dataclass
class Registro:
    fecha: str
    intensidad: int
    categoria: str
    texto: str = ""


def normalizar(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def tokenizar(linea):
    tokens, errores = [], []
    for m in _MASTER.finditer(linea):
        tipo = m.lastgroup
        if tipo == "ESPACIO":
            continue
        if tipo == "ERROR":
            errores.append(Error("LEX_CARACTER_INVALIDO", "linea", f"Carácter no permitido en posición {m.start()}"))
            continue
        tokens.append(Token(tipo, m.group(), m.start()))
    return tokens, errores


def parsear(tokens):
    """<registro> ::= FECHA NUMERO PALABRA [TEXTO]"""
    esperado = ["FECHA", "NUMERO", "PALABRA"]
    for i, tipo in enumerate(esperado):
        if i >= len(tokens) or tokens[i].tipo != tipo:
            return None, [Error("SINT_ESPERABA_" + tipo, tipo.lower(), f"Se esperaba {tipo}")]
    resto = tokens[3:]
    texto = ""
    if resto:
        if resto[0].tipo != "TEXTO" or len(resto) > 1:
            return None, [Error("SINT_TOKEN_SOBRANTE", "texto", "Tokens inesperados al final del registro")]
        texto = resto[0].valor[1:-1]
    f, n, c = tokens[:3]
    return Registro(f.valor, int(n.valor), c.valor, texto), []


def validar(reg, hoy=None):
    hoy = hoy or date.today()
    errores = []
    try:
        if date.fromisoformat(reg.fecha) > hoy:
            errores.append(Error("SEM_FECHA_FUTURA", "fecha", "La fecha no puede ser futura"))
    except ValueError:
        errores.append(Error("SEM_FECHA_INVALIDA", "fecha", "Fecha inexistente"))
    if not 1 <= reg.intensidad <= 10:
        errores.append(Error("SEM_INTENSIDAD_RANGO", "intensidad", "La intensidad debe estar entre 1 y 10"))
    cat = normalizar(reg.categoria)
    if cat not in CATEGORIAS:
        errores.append(Error("SEM_CATEGORIA_INVALIDA", "categoria", "Categoría no reconocida"))
    else:
        reg.categoria = cat
    if len(reg.texto) > TEXTO_MAX:
        errores.append(Error("SEM_TEXTO_LARGO", "texto", "Máximo 200 caracteres"))
    return errores


def interpretar(linea, hoy=None):
    tokens, e1 = tokenizar(linea)
    if e1:
        return {"valido": False, "tokens": tokens, "registro": None, "errores": e1}
    reg, e2 = parsear(tokens)
    if e2:
        return {"valido": False, "tokens": tokens, "registro": None, "errores": e2}
    e3 = validar(reg, hoy)
    return {"valido": not e3, "tokens": tokens, "registro": reg if not e3 else None, "errores": e3}
```

Casos que deben pasar en `test_interprete.py`: `2026-10-12 8 Ansiedad "No dormí bien"` (válido); `2026-10-12 5 Estrés` (válido, sin texto); `... 11 Calma` → `SEM_INTENSIDAD_RANGO`; `... 5 Enojo` → `SEM_CATEGORIA_INVALIDA`; fecha posterior a `hoy` → `SEM_FECHA_FUTURA`; `2026-02-31 5 Calma` → `SEM_FECHA_INVALIDA`; `2026-10-12 5` → `SINT_ESPERABA_PALABRA`; `... Calma "a" "b"` → `SINT_TOKEN_SOBRANTE`; `... Calma @` → `LEX_CARACTER_INVALIDO`; texto de 201 caracteres → `SEM_TEXTO_LARGO`.

### 9.4 `reglas.py` — constantes documentadas (nada de números sueltos en el código)

```python
# --- Alerta por intensidad sostenida ---
VENTANA_REGISTROS = 4            # se miran los últimos N registros
INTENSIDAD_ALTA = 8              # intensidad >= este valor cuenta como "alta"
MIN_REGISTROS_ALTOS = 3          # cuántos de la ventana deben ser altos
CATEGORIAS_DIFICILES = {"ansiedad", "tristeza", "estres"}
CATEGORIAS_POSITIVAS = {"calma", "alegria"}

# --- Alerta por señal de IA (solo se usa si la respuesta fue válida) ---
UMBRAL_CONFIANZA_IA = 0.75

# --- Tendencia de la gráfica ---
# valencia de un registro: +intensidad si categoría positiva, -intensidad si difícil.
# promedio >= +UMBRAL_TENDENCIA => "positiva"; <= -UMBRAL_TENDENCIA => "negativa"; si no, "neutral".
UMBRAL_TENDENCIA = 2

# --- Urgencia (protocolo ante peligro inmediato) ---
PALABRAS_URGENCIA = ["quiero morir", "no quiero vivir", "quitarme la vida", "hacerme daño", "suicid"]
```

Funciones (en `reglas.py` o `emociones/estadisticas.py`, **puras**, sin tocar la base de datos):

- `evaluar_alerta(registros_recientes) -> {"activa": bool, "motivo": "intensidad_sostenida"|"senal_ia"|None}` — `registros_recientes` va del más nuevo al más viejo. Activa si, de los últimos `VENTANA_REGISTROS`, al menos `MIN_REGISTROS_ALTOS` tienen `intensidad >= INTENSIDAD_ALTA` **y** categoría en `CATEGORIAS_DIFICILES`; **o** si el último registro tiene `ia_patron_riesgo=True` con `ia_confianza >= UMBRAL_CONFIANZA_IA`. El `motivo` es interno: **no se envía al cliente**.
- `detectar_urgencia(texto) -> bool` — coincidencia simple (sin acentos, minúsculas) con `PALABRAS_URGENCIA`. Es una heurística mínima, no una garantía; si es `True`, la respuesta lleva `"urgente": true` y el cliente abre de inmediato el modal de recursos.
- `calcular_tendencia(registros) -> "positiva"|"neutral"|"negativa"`.

Por qué la tendencia usa valencia y no solo intensidad: una intensidad 9 de *Alegría* no debe pintar la gráfica de rojo.

### 9.5 Flujo `pipeline.procesar_registro(usuario, datos, hoy)`

1. Validar forma con el serializer (campos presentes, `texto_libre` ≤ 200). Si falla → 400.
2. Construir la línea y llamar a `interpretar(linea, hoy)`.
3. Guardar `AnalisisLog` (siempre, válido o no; **sin texto**). Si hay errores → 400 con `errores`.
4. Si ya existe registro del día → 409.
5. Guardar `Registro` con los valores **normalizados** del intérprete (categoría canónica).
6. Si hay `texto_libre` → `ai_service.clasificar(texto)`; guardar `SolicitudIA`; en éxito, llenar `ia_*` del registro; en fallo, dejar `ia_*` vacíos.
7. `detectar_urgencia(texto)`; `evaluar_alerta(últimos registros)`.
8. Armar la respuesta de la sección 8 usando `mensajes.py`.

`mensajes.py`: tres frases prudentes (para `negativo`, `neutro`, `positivo`) y una para "no disponible". Lenguaje cálido, sin diagnóstico, sin la palabra "riesgo".

### 9.6 `POST /interprete/analizar/` (demo para la defensa)

Recibe `{"linea": "2026-10-12 8 Ansiedad \"No dormí bien\""}` y devuelve los tokens (`tipo`, `valor`, `pos`), el árbol (`registro` → `fecha`, `intensidad`, `categoria`, `texto`) y los errores. **No guarda nada.** Sirve para mostrar el intérprete funcionando ante el profesor (página opcional `interprete.html` en el cliente).

---

## 10. Servicio de IA (`ai_service.py`)

`PROVEEDOR_IA`:

| Valor | Comportamiento |
|---|---|
| `desactivado` (por defecto si falta) | No llama a nada. `SolicitudIA` con `estado=fallida`, `error_tipo=desactivada`. |
| `simulado` | Respuesta determinista por palabras clave (ej. "no pude dormir", "agobiado" → negativo). Permite probar todo el flujo sin clave ni red. |
| `openai` | Llama a la API con `OPENAI_API_KEY` y `IA_MODELO` leídos del entorno, timeout `IA_TIMEOUT_SEGUNDOS`, pidiendo **solo JSON** con el esquema de abajo. |

Esquema que la respuesta **debe** cumplir (si no, se descarta como `error_tipo=formato`):

```json
{"etiqueta_sentimiento": "negativo", "confianza": 0.78, "patron_riesgo": true, "explicacion_breve": "..."}
```

- `etiqueta_sentimiento` ∈ `positivo | neutro | negativo`; `confianza` número entre 0 y 1; `patron_riesgo` booleano; `explicacion_breve` cadena ≤ 200.
- `explicacion_breve` se valida pero **no se almacena**.
- Al proveedor se envía **solo** el `texto_libre` (sin nombre, correo ni id). Mensaje de sistema: clasificar el sentimiento, **no diagnosticar**, responder solo con el JSON.
- Cualquier excepción, timeout o respuesta inválida → falla controlada (regla 6 de la sección 2). Nunca propagar el error al usuario ni bloquear el guardado.

---

## 11. Interfaz del cliente (`frontend_cliente/`)

HTML/CSS/JS puro, **mobile-first** (ancho máximo 460 px centrado), sin frameworks. Todas las llamadas pasan por `js/api.js`:

- Antes del primer POST, `GET /api/v1/auth/csrf/`; leer la cookie `csrftoken` y enviarla en `X-CSRFToken`.
- `fetch(..., {credentials: "same-origin"})`.
- Si una respuesta es 401/403 por sesión, redirigir a `login.html`.

Guardia de sesión en `app.html`: `GET /auth/me/`; si no hay sesión o `rol != "usuario"`, redirigir a `login.html`.

### Pantallas

- **`login.html`** / **`registro.html`**: formularios simples; errores del API mostrados bajo el campo; aviso legal al pie.
- **`app.html`**, barra superior fija: logo "Bitácora" a la izquierda, pestañas **Registrar · Historial · Estadísticas** (navegación por `#hash`, sin recargar), ícono de perfil con menú "Cerrar sesión" a la derecha.
  - **Registrar:** saludo con la fecha; tarjeta con fecha (por defecto hoy, `max` = hoy), slider 1–10 con número grande que cambia de color/etiqueta (leve · moderada · alta · muy alta), 5 chips de categoría (uno a la vez), textarea opcional con contador `n/200`, botón "Guardar registro" de ancho completo. Debajo, la **racha** (7 segmentos L–D, `GET /racha/`). Tras guardar: mostrar `analisis_texto.mensaje` y, si `alerta.activa`, el banner.
  - **Historial:** lista de tarjetas (fecha, categoría con color/ícono, intensidad, primeras palabras del texto) con **barra lateral** verde/ámbar/roja según intensidad (1–4 / 5–7 / 8–10). Botón "Cargar más" para la paginación.
  - **Estadísticas:** 3 tarjetas (intensidad promedio, categoría más frecuente, días registrados este mes) y gráfica de línea SVG de `serie` con selector 7/30 días; la línea se colorea según `tendencia` (positiva = verde `#8FB6A6`, neutral = ámbar `#E3A857`, negativa = coral `#D97D6C`); los días con `null` interrumpen la línea.
- **Banner de alerta** (`alerta.js`): fondo ámbar suave, texto: *"Hemos notado que has tenido días difíciles. ¿Quieres ver recursos de apoyo?"* con botones **Ver recursos** y **Cerrar** (cerrar lo oculta el resto de la sesión con `sessionStorage`). Se consulta `GET /alerta/` al cargar la app y tras cada guardado.
- **Modal de recursos:** lista de `GET /recursos-apoyo/`. Si el guardado devuelve `urgente: true`, se abre automáticamente con tono sereno.
- **Pie de página** en todas las pantallas: "Esta herramienta no sustituye atención profesional."

### Reglas de interfaz

- Prohibido en pantalla: "riesgo", "trastorno", "diagnóstico", "alerta roja". El rojo/coral se usa solo en barras de intensidad alta y gráfica.
- **No usar `toISOString()` para la fecha de hoy** (devuelve UTC y en Tijuana, por la tarde, daría el día siguiente). Construirla con `getFullYear()`, `getMonth()+1`, `getDate()`.
- Usar `textContent` (nunca `innerHTML`) para pintar texto del usuario.
- Elementos accesibles: `<button>`, `<label for>`, foco visible, contraste AA, `aria-label` en íconos sin texto, respetar `prefers-reduced-motion`.

### Tokens de diseño (en variables CSS `:root`)

```
--fondo:#F5F4EF   --superficie:#FFFFFF   --texto:#26332F   --texto-suave:#5B6760   --tenue:#93A098   --linea:#E2E7DE
--primario:#4F7A64   --primario-hover:#3B6650   --azul:#7FA6B8
--int-baja:#8FB6A6   --int-media:#E3A857   --int-alta:#D97D6C
--alerta-fondo:#FBF0DD   --alerta-borde:#F1DDB4   --alerta-texto:#7A5417
--cat-ansiedad:#7FA6B8   --cat-tristeza:#8593C4   --cat-estres:#D9936C   --cat-calma:#6E9B82   --cat-alegria:#CBA23A
Radios: tarjeta 20px · tarjeta pequeña 14px · chips y botones 999px
Fuentes (Google Fonts): "Fraunces" para títulos y números grandes; "Work Sans" para la interfaz
```

---

## 12. Interfaz administrativa (`frontend_admin/`)

Separada del cliente: carpeta, login y archivos JS propios (`api.js` duplicado a propósito). Estilo más "de herramienta": barra lateral oscura (`#232D28`, texto `#D7DED9`), contenido sobre `#F7F8F6`, tablas con insignias de estado (verde = correcto, ámbar = pendiente, coral = fallo/denegado), tipografía monoespaciada (JetBrains Mono) para tokens e identificadores.

Guardia en `panel.html`: `GET /auth/me/`; si `rol != "administrador"` → `login.html`. El login llama a `/admin/auth/login/`.

Secciones de la barra lateral (una sola página, cambio por `#hash`):

1. **Usuarios** — tabla (nombre, correo, rol, estado, fecha de alta, nº de registros) con búsqueda y filtro de activos; botones: crear cuenta, activar/desactivar, asignar rol administrador (con diálogo de confirmación), eliminar (confirmación fuerte). **Nunca** muestra contenido de registros.
2. **Autenticación y sesiones** — eventos `categoria=sesion` (inicio/cierre de sesión, intentos fallidos, permisos denegados) con insignia de resultado. Aviso fijo: "No se muestran contraseñas, claves, cookies ni tokens completos."
3. **Analizador lingüístico** — últimos `AnalisisLog`: fecha, válido/no, nº de tokens, conteo por tipo de token, estado de cada campo (`ok/error`) y códigos de error. Encabezado de la sección: "Tokens léxicos" (distinto de las sesiones).
4. **Integración con IA** — resumen (total, fallidas, tiempo promedio) y tabla de solicitudes (estado, tiempo, esquema válido, tipo de error). Muestra el JSON de ejemplo del esquema, **no** respuestas reales.
5. **Auditoría** — eventos `categoria=admin`: fecha/hora, acción, resultado, actor, objetivo.

---

## 13. Seguridad — lista de verificación

- [ ] `AUTH_USER_MODEL` definido antes de la primera migración.
- [ ] Registro público ignora `rol` (hay prueba que lo demuestra).
- [ ] Login de cliente rechaza administradores y viceversa.
- [ ] POST de login/registro/logout exige token CSRF (hay prueba: sin token → 403).
- [ ] Toda vista de datos personales filtra por `request.user`; el acceso a un id ajeno devuelve 404.
- [ ] Administrador recibe 403 en `/registros/`, `/estadisticas/`, `/racha/`, `/alerta/`.
- [ ] Contraseñas con los validadores de Django; nunca registradas en ningún log.
- [ ] `texto_libre` no aparece en `AnalisisLog`, `SolicitudIA` ni `EventoAuditoria` (hay prueba).
- [ ] Throttling activo en login y registro.
- [ ] `.env` fuera del repositorio; ninguna clave en JavaScript.
- [ ] Salida de IA validada contra el esquema antes de usarse.
- [ ] En el frontend, texto del usuario se pinta con `textContent`.

---

## 14. Pruebas obligatorias (`python manage.py test`)

- **`analizador/tests/test_interprete.py`** — los 10 casos de la sección 9.3 (Python puro).
- **`cuentas/tests/test_auth.py`** — registro público con `rol="administrador"` en el cuerpo crea un usuario normal; login cliente rechaza admin; login admin rechaza usuario; POST sin CSRF → 403; `/auth/me/` sin sesión → 403/401; `createsuperuser` produce `rol=administrador`.
- **`cuentas/tests/test_admin_usuarios.py`** — usuario normal recibe 403 en `/admin/*`; admin no puede desactivarse/eliminarse a sí mismo ni dejar el sistema sin admins; `asignar-rol` genera evento de auditoría.
- **`emociones/tests/test_registros.py`** — crear (201), fecha futura (400), intensidad 11 (400), categoría inválida (400), duplicado del día (409), PUT edita; usuario A no ve/edita/borra registros de B (404); administrador → 403 en `/registros/`.
- **`emociones/tests/test_estadisticas.py`** — promedio, categoría frecuente, días del mes, racha (con y sin hoy), `serie` con `null`, tendencia (caso *Alegría 9* ⇒ positiva).
- **`emociones/tests/test_alerta.py`** — 3 de 4 registros con intensidad ≥ 8 en categorías difíciles ⇒ activa; 2 de 4 ⇒ no; Alegría 9 ×4 ⇒ no; IA con `patron_riesgo` y confianza 0.9 ⇒ activa; confianza 0.5 ⇒ no.
- **`analizador/tests/test_ai_service.py`** — respuesta válida; JSON inválido, campo faltante, confianza 1.7, excepción y timeout ⇒ descartada, registro guardado, `SolicitudIA.estado=fallida`, sin alerta por IA.
- **`analizador/tests/test_privacidad_logs.py`** — crear un registro con texto `SECRETO-12345` y comprobar que esa cadena no está en ningún campo de `AnalisisLog`, `SolicitudIA` ni `EventoAuditoria`.
- **`auditoria/tests/test_monitor.py`** — endpoints de monitor solo para administrador; no devuelven texto de registros.

---

## 15. Fases de trabajo

**Fase 0 — Esqueleto.** Crear carpetas, entorno, proyecto Django, las 4 apps, `settings.py`, `urls.py`, `api_urls.py`, `.env.example`, `.gitignore`.
*Hecho cuando:* `runserver` arranca y `http://127.0.0.1:8000/api/v1/auth/csrf/` responde `{"detail":"ok"}`.

**Fase 1 — Cuentas y permisos.** `Usuario`, `crear_admin`, permisos, registro/login/login-admin/logout/me, CSRF, throttling, eventos de sesión en auditoría (crear aquí el modelo y el servicio de auditoría).
*Hecho cuando:* pasan `test_auth.py` y las pruebas de permisos básicos.

**Fase 2 — Intérprete.** `lexer.py`, `parser.py`, `semantic.py`, `interprete.py`, `reglas.py`, `mensajes.py` y `test_interprete.py`. Sin tocar la base de datos.
*Hecho cuando:* los 10 casos pasan y se puede ejecutar `interpretar(...)` desde una consola de Python.

**Fase 3 — Registros, estadísticas y alerta.** Modelo `Registro`, `AnalisisLog`, `pipeline.py` (sin IA aún), endpoints de `/registros/`, `/estadisticas/`, `/racha/`, `/alerta/`, `/recursos-apoyo/`, `/interprete/analizar/`.
*Hecho cuando:* pasan `test_registros.py`, `test_estadisticas.py`, `test_alerta.py`.

**Fase 4 — Administración y monitoreo.** `views_admin.py` de cuentas, vistas de auditoría y monitor (`analizador`, `ia`).
*Hecho cuando:* pasan `test_admin_usuarios.py` y `test_monitor.py`.

**Fase 5 — IA.** `ai_service.py` con `desactivado` y `simulado` primero, luego `openai`; `SolicitudIA`; integrar en el pipeline.
*Hecho cuando:* pasan `test_ai_service.py` y `test_privacidad_logs.py`, y con `PROVEEDOR_IA=simulado` el flujo completo devuelve `analisis_texto.mensaje`.

**Fase 6 — Interfaz del cliente.** Pantallas de la sección 11 contra la API real.
*Hecho cuando:* en `http://127.0.0.1:8000/` se puede crear cuenta, iniciar sesión, guardar un registro, ver historial y estadísticas, y disparar el banner de alerta con 3 registros de intensidad 8–9 en Ansiedad/Estrés/Tristeza.

**Fase 7 — Interfaz administrativa.** Pantallas de la sección 12.
*Hecho cuando:* en `http://127.0.0.1:8000/panel/` el administrador gestiona cuentas, ve las 4 secciones de monitoreo, y un usuario normal no puede entrar.

**Fase 8 — Cierre.** `README.md` con: requisitos, instalación, cómo crear el administrador, variables de entorno, URLs, cómo correr pruebas, limitación de la sesión única por navegador, "Decisiones" tomadas y lista de pendientes.
*Hecho cuando:* una persona nueva puede levantar el proyecto siguiendo solo el README.

---

## 16. Recursos de apoyo (`emociones/recursos_apoyo.py`)

```python
RECURSOS_APOYO = [
    {"nombre": "Línea de la Vida", "telefono": "800 911 2000", "detalle": "Atención emocional y salud mental, 24 horas."},
    {"nombre": "SAPTEL", "telefono": "55 5259 8121", "detalle": "Apoyo en crisis emocional por teléfono, 24 horas."},
    {"nombre": "Emergencias", "telefono": "911", "detalle": "Si hay peligro inmediato."},
    {"nombre": "Psicología de tu institución", "telefono": "", "detalle": "Pregunta por el servicio de apoyo psicológico de tu escuela."},
]
```

> **Verificar antes de usar con personas reales:** los números provienen del directorio de apoyo psicológico 2026 de la UAM (ficha actualizada en abril de 2026) y deben confirmarse en los canales oficiales. Mantener esta lista en un solo archivo para poder actualizarla sin tocar el resto del código.

---

## 17. Definición de "terminado" de la versión básica

1. `python manage.py test` pasa completo.
2. Con `PROVEEDOR_IA=simulado`, el recorrido usuario completo funciona en `/`.
3. El recorrido administrador completo funciona en `/panel/`, y un usuario normal no puede acceder.
4. Ningún endpoint ni pantalla expone registros de otras personas, ni siquiera al administrador.
5. La lista de seguridad (sección 13) está marcada.
6. El `README.md` está completo.
