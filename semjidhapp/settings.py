"""
Django settings for semjidhapp project.
"""

import os
from pathlib import Path

import dj_database_url
import environ


BASE_DIR = Path(__file__).resolve().parent.parent


# Lê variáveis do arquivo .env local.
# No Render, as mesmas variáveis serão criadas no painel do serviço.
env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# ---------------------------------------------------------
# Segurança e ambiente
# ---------------------------------------------------------

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)


# Local: localhost e 127.0.0.1.
# Render: o próprio Render fornece RENDER_EXTERNAL_HOSTNAME.
# Produção/domínio próprio: adicione no Render usando ALLOWED_HOSTS.
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

ALLOWED_HOSTS.extend(env.list("ALLOWED_HOSTS", default=[]))


# Necessário para requisições POST feitas por domínios externos
# em produção. No Render, adicionaremos a URL depois do primeiro deploy.
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])


# ---------------------------------------------------------
# Aplicações
# ---------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "viagens",
    "widget_tweaks",
]


# ---------------------------------------------------------
# Middlewares
# WhiteNoise deve ficar imediatamente após SecurityMiddleware.
# ---------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "semjidhapp.urls"


# ---------------------------------------------------------
# Templates
# ---------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "semjidhapp.wsgi.application"


# ---------------------------------------------------------
# Banco de dados
#
# Local:
# DATABASE_URL=sqlite:///db.sqlite3
#
# Render:
# DATABASE_URL=postgresql://... (URL do Session Pooler do Supabase)
# ---------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=env(
            "DATABASE_URL",
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        ),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ---------------------------------------------------------
# Validação de senhas
# ---------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ---------------------------------------------------------
# Idioma, data e horário
# ---------------------------------------------------------

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------
# Arquivos estáticos
# ---------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Django 5.1 recomenda STORAGES em vez de STATICFILES_STORAGE.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ---------------------------------------------------------
# Configurações do sistema
# ---------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"


# ---------------------------------------------------------
# E-mail
#
# DEBUG=True: não envia e-mail; escreve a mensagem no terminal.
# DEBUG=False: usa SMTP e lê as credenciais das variáveis de ambiente.
# ---------------------------------------------------------

DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="viagens@semjidh.rn.gov.br",
)

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
    
N8N_WEBHOOK_URL = env(
    "N8N_WEBHOOK_URL",
    default="",
)

N8N_WEBHOOK_SECRET = env(
    "N8N_WEBHOOK_SECRET",
    default="",
)