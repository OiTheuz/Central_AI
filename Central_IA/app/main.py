import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import app_lojista, auth, admin, dashboards

from app.database import engine, Base, SessionLocal

# Importa os models para garantir que o Base.metadata conhece todas as tabelas
from app.models import Merchant, ActiveSession  # noqa: F401

# Importa os routers
from app.routers import webhook_router, lojistas_router, agendamentos_router, custos

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
# BACKGROUND TASK: TIMEOUT DE INATIVIDADE (1 HORA)
# Roda a cada 5 minutos e encerra sessões sem resposta há
# mais de 1h, enviando a mensagem de encerramento ao cliente.
# Nota: single-process safe. Para multi-worker, migrar para
# Celery Beat ou APScheduler com Redis.
# =========================================================

def _processar_timeouts_sync() -> list[dict]:
    """
    Função SÍNCRONA que roda em thread pool (via asyncio.to_thread).
    Encerra sessões expiradas no banco e retorna a lista de clientes
    para notificação. Separar DB e HTTP evita manter a sessão aberta
    durante chamadas de rede — prevenindo connection pool exhaustion.
    """
    from sqlalchemy import text

    LIMITE_INATIVIDADE = timedelta(hours=1)
    clientes_para_notificar: list[dict] = []

    db = SessionLocal()
    try:
        limite = datetime.now() - LIMITE_INATIVIDADE

        sessoes_expiradas = db.execute(
            text("""
                SELECT id, telefone_cliente
                FROM public.active_sessions
                WHERE ativo = TRUE
                  AND ultima_interacao IS NOT NULL
                  AND ultima_interacao < :limite
            """),
            {"limite": limite}
        ).mappings().fetchall()

        if not sessoes_expiradas:
            return []

        ids_expirados = [s["id"] for s in sessoes_expiradas]
        logger.info(
            "Timeout: encerrando %d sessão(ões) inativas. IDs: %s",
            len(ids_expirados), ids_expirados
        )

        # Encerra todas as sessões de uma vez (batch update)
        db.execute(
            text("""
                UPDATE public.active_sessions
                SET ativo = FALSE
                WHERE id = ANY(:ids)
            """),
            {"ids": ids_expirados}
        )
        db.commit()

        # Coleta os telefones para notificar APÓS o commit —
        # se o WhatsApp falhar, o banco já está correto.
        clientes_para_notificar = [
            {"telefone": s["telefone_cliente"]} for s in sessoes_expiradas
        ]

    except Exception as e:
        logger.error("Erro ao processar timeouts no banco: %s", e)
        db.rollback()
    finally:
        db.close()

    return clientes_para_notificar


def _enviar_whatsapp_timeout_sync(telefone: str, mensagem: str) -> None:
    """Função SÍNCRONA de envio WhatsApp — executada em thread pool."""
    from app.services.whatsapp_service import enviar_mensagem_whatsapp
    enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem)


async def _verificar_timeouts_de_inatividade():
    """
    Coroutine principal do loop de timeout.
    Todo I/O bloqueante (DB + HTTP) roda em thread pool via asyncio.to_thread,
    garantindo que o event loop nunca seja travado.
    """
    MENSAGEM_TIMEOUT = (
        "Como não tivemos mais interação, a conversa será encerrada. "
        "Qualquer coisa, pode enviar uma nova mensagem! 😊"
    )

    while True:
        await asyncio.sleep(300)  # verifica a cada 5 minutos
        try:
            # 1. Encerrar sessões no banco (I/O síncrono → thread pool)
            clientes = await asyncio.to_thread(_processar_timeouts_sync)

            # 2. Notificar cada cliente via WhatsApp (I/O síncrono → thread pool)
            for cliente in clientes:
                telefone = cliente["telefone"]
                try:
                    await asyncio.to_thread(
                        _enviar_whatsapp_timeout_sync, telefone, MENSAGEM_TIMEOUT
                    )
                    logger.info("Mensagem de timeout enviada para: %s", telefone)
                except Exception as e:
                    logger.warning(
                        "Falha ao enviar timeout WhatsApp para %s: %s", telefone, e
                    )

        except Exception as e:
            logger.error("Erro inesperado no loop de timeout: %s", e)



# =========================================================
# LIFESPAN — inicializa e encerra a background task
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando background task de verificação de timeouts...")
    task = asyncio.create_task(_verificar_timeouts_de_inatividade())
    yield
    logger.info("Encerrando background task de timeouts...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# =========================================================
# CRIA TABELAS

Base.metadata.create_all(bind=engine)

# =========================================================
# APP

app = FastAPI(title="API Central de Agendamento", lifespan=lifespan)

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
app.include_router(admin.router)       # /admin/estabelecimento (requer JWT admin)
app.include_router(dashboards.router)  # /api/dashboards/...
app.include_router(custos.router)

# =========================================================
# HEALTH CHECK

@app.get("/")
def home():
    return {
        "status": "online",
        "api": "API Central de Agendamento"
    }
