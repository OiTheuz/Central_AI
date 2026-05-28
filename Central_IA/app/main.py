import logging
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import app_lojista, auth

from app.database import engine, Base

# Importa os models para garantir que o Base.metadata conhece todas as tabelas
from app.models import Merchant, ActiveSession  # noqa: F401

# Importa os routers
from app.routers import webhook_router, lojistas_router, agendamentos_router

# =========================================================
# LOGGING — substitui print() por logs estruturados
# Em produção, ajuste o level para WARNING e integre com
# um serviço externo (Sentry, Datadog, etc.)
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# =========================================================
# CRIA TABELAS

Base.metadata.create_all(bind=engine)

# =========================================================
# APP

app = FastAPI(title="API Central de Agendamento")

# =========================================================
# CORS — permite o app mobile/web acessar a API
# ⚠️ Em produção, substitua ["*"] pelos domínios reais:
# allow_origins=["https://seu-dominio.com", "exp://..."]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# REGISTRA ROUTERS

app.include_router(auth.router)         # /api/auth/login, /api/auth/me
app.include_router(webhook_router)
app.include_router(app_lojista.router)  # /api/mobile/...
app.include_router(lojistas_router)
app.include_router(agendamentos_router)

# =========================================================
# HEALTH CHECK

@app.get("/")
def home():
    return {
        "status": "online",
        "api": "API Central de Agendamento"
    }
