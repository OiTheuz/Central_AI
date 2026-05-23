from fastapi import FastAPI
from app.routers import app_lojista

from app.database import engine, Base

# Importa os models para garantir que o Base.metadata conhece todas as tabelas
from app.models import Merchant, ActiveSession  # noqa: F401

# Importa os routers
from app.routers import webhook_router, lojistas_router, agendamentos_router

# =========================================================
# CRIA TABELAS

Base.metadata.create_all(bind=engine)

# =========================================================
# APP

app = FastAPI(title="API Central de Agendamento")

# =========================================================
# REGISTRA ROUTERS

app.include_router(webhook_router)
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
