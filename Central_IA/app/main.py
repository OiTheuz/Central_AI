import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import app_lojista, auth, admin, dashboards, site
from app.services.websocket_manager import manager
from app.services.auth_service import decodificar_token_jwt

from app.database import engine, Base, SessionLocal

# Importa os models para garantir que o Base.metadata conhece todas as tabelas
from app.models import Merchant, ActiveSession  # noqa: F401

# Importa os routers
from app.routers import webhook_router, lojistas_router, agendamentos_router, custos, chat_router, ws_chat_router, onboarding, billing

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
                SELECT id, telefone_cliente, loja_atual
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
            {"telefone": s["telefone_cliente"], "schema": s["loja_atual"]} for s in sessoes_expiradas
        ]

    except Exception as e:
        logger.error("Erro ao processar timeouts no banco: %s", e)
        db.rollback()
    finally:
        db.close()

    return clientes_para_notificar


def _enviar_whatsapp_timeout_sync(telefone: str, mensagem: str, schema_name: str) -> None:
    """Função SÍNCRONA de envio WhatsApp — executada em thread pool."""
    from app.services.whatsapp_service import enviar_mensagem_whatsapp
    from app.database import SessionLocal
    from app.models import Merchant
    db = SessionLocal()
    try:
        main_merchant = db.query(Merchant).filter(Merchant.nome_do_schema == schema_name, Merchant.loja_pai_id == None).first()
        token = None
        phone_id = None
        if main_merchant:
            token = main_merchant.meta_access_token
            phone_id = main_merchant.meta_phone_id
            
        enviar_mensagem_whatsapp(
            numero_destino=telefone, 
            texto=mensagem,
            phone_number_id=str(phone_id) if phone_id else None,
            token=token
        )
    finally:
        db.close()


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
                schema_name = cliente["schema"]
                try:
                    await asyncio.to_thread(
                        _enviar_whatsapp_timeout_sync, telefone, MENSAGEM_TIMEOUT, schema_name
                    )
                    logger.info("Mensagem de timeout enviada para: %s", telefone)
                except Exception as e:
                    logger.warning(
                        "Falha ao enviar timeout WhatsApp para %s: %s", telefone, e
                    )

        except Exception as e:
            logger.error("Erro inesperado no loop de timeout: %s", e)



# =========================================================
# BACKGROUND TASK: LEMBRETES DIÁRIOS
# =========================================================

def _processar_lembretes_sync(tipo: str):
    from sqlalchemy import text
    from datetime import datetime
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        from backports.zoneinfo import ZoneInfo  # type: ignore # Python 3.8 fallback se necessário
    from app.services.push_service import enviar_notificacao_push
    
    db = SessionLocal()
    fuso = ZoneInfo("America/Sao_Paulo")
    hoje = datetime.now(fuso).date()
    
    try:
        merchants = db.execute(
            text("""
                SELECT id, nome_loja, nome_do_schema, push_token 
                FROM merchant 
                WHERE push_token IS NOT NULL 
                  AND notificacoes_push_enabled = TRUE 
                  AND notificacoes_lembretes = TRUE
            """)
        ).mappings().fetchall()
        
        for m in merchants:
            schema = m["nome_do_schema"]
            try:
                count_res = db.execute(
                    text(f"""
                        SELECT COUNT(*) as qtd
                        FROM {schema}.appointments
                        WHERE data_agendamento = :hoje
                          AND status NOT IN ('cancelado', 'recusado')
                    """),
                    {"hoje": hoje}
                ).fetchone()
                
                qtd = count_res[0] if count_res else 0
                
                if tipo == "matinal":
                    if qtd > 0:
                        enviar_notificacao_push(
                            push_token=m["push_token"],
                            titulo="☀️ Bom dia!",
                            corpo=f"Você tem {qtd} agendamento(s) para hoje. Tenha um ótimo dia de trabalho!",
                            dados={"tela": "calendar"}
                        )
                    else:
                        enviar_notificacao_push(
                            push_token=m["push_token"],
                            titulo="☀️ Bom dia!",
                            corpo="Você ainda não tem agendamentos para hoje. Aproveite para divulgar seus serviços!",
                            dados={"tela": "calendar"}
                        )
                elif tipo == "noturno":
                    enviar_notificacao_push(
                        push_token=m["push_token"],
                        titulo="🌙 Resumo do dia",
                        corpo=f"Hoje você teve {qtd} agendamento(s) programado(s). Bom descanso!",
                        dados={"tela": "calendar"}
                    )
            except Exception as e:
                logger.error("Erro ao processar lembretes para schema %s: %s", schema, e)
                
    except Exception as e:
        logger.error("Erro geral no loop de lembretes: %s", e)
    finally:
        db.close()

async def _loop_de_lembretes_diarios():
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        from backports.zoneinfo import ZoneInfo  # type: ignore
    from datetime import datetime
    fuso = ZoneInfo("America/Sao_Paulo")
    
    ultimo_minuto_disparado = None
    
    while True:
        agora = datetime.now(fuso)
        hh_mm = agora.strftime("%H:%M")
        
        if hh_mm == "07:30" and ultimo_minuto_disparado != "07:30":
            ultimo_minuto_disparado = hh_mm
            logger.info("Disparando lembretes matinais...")
            await asyncio.to_thread(_processar_lembretes_sync, "matinal")
            
        elif hh_mm == "20:00" and ultimo_minuto_disparado != "20:00":
            ultimo_minuto_disparado = hh_mm
            logger.info("Disparando lembretes noturnos...")
            await asyncio.to_thread(_processar_lembretes_sync, "noturno")
            
        elif hh_mm not in ["07:30", "20:00"]:
            ultimo_minuto_disparado = None
            
        await asyncio.sleep(30)


# =========================================================
# BACKGROUND TASK: LEMBRETES IA (A CADA MINUTO)
# =========================================================

async def _loop_de_lembretes_1_minuto():
    from scripts.check_lembretes_pos import run_lembretes
    from scripts.check_lembretes_pre import run_lembretes_pre
    while True:
        try:
            await run_lembretes()
        except Exception as e:
            logger.error("Erro no loop de lembretes pos-servico: %s", e)
            
        try:
            await run_lembretes_pre()
        except Exception as e:
            logger.error("Erro no loop de lembretes pre-servico: %s", e)
            
        await asyncio.sleep(60)


# =========================================================
# LIFESPAN — inicializa e encerra as background tasks
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando background tasks (Timeouts e Lembretes)...")
    task_timeouts = asyncio.create_task(_verificar_timeouts_de_inatividade())
    task_lembretes = asyncio.create_task(_loop_de_lembretes_diarios())
    task_1_minuto = asyncio.create_task(_loop_de_lembretes_1_minuto())
    yield
    logger.info("Encerrando background tasks...")
    task_timeouts.cancel()
    task_lembretes.cancel()
    task_1_minuto.cancel()
    await asyncio.gather(task_timeouts, task_lembretes, task_1_minuto, return_exceptions=True)


# =========================================================
# CRIA TABELAS

Base.metadata.create_all(bind=engine)

# =========================================================
# APP

app = FastAPI(title="API Central de Agendamento", lifespan=lifespan)

import os
from fastapi.staticfiles import StaticFiles

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
app.include_router(site.router)
app.include_router(chat_router)
app.include_router(ws_chat_router)
app.include_router(onboarding.router)
app.include_router(billing.router, prefix="/api")

# =========================================================
# HEALTH CHECK E ARQUIVOS ESTÁTICOS

from fastapi.staticfiles import StaticFiles
import os

# Certifica-se de que a pasta uploads existe para evitar erro no mount
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def home():
    return {
        "status": "online",
        "api": "API Central de Agendamento"
    }

# =========================================================
# PÁGINAS PÚBLICAS
# =========================================================

@app.get("/api/privacidade", response_class=HTMLResponse)
def privacidade():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Política de Privacidade</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; padding: 30px; max-width: 800px; margin: auto; color: #333; }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 40px; }
            h2 { color: #34495e; margin-top: 30px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
            p { margin-bottom: 15px; text-align: justify; }
            .container { background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            body { background: #f9f9f9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Termos e Política de Privacidade</h1>
            <p>Bem-vindo à Central IA! Para continuarmos garantindo a melhor experiência e segurança, apresentamos a nossa Política de Privacidade.</p>
            
            <h2>1. Coleta de Dados</h2>
            <p>Coletamos informações necessárias para o funcionamento do agendamento via WhatsApp, incluindo números de telefone dos clientes e o histórico das conversas para que a Inteligência Artificial possa atuar de forma eficiente no atendimento e marcação de horários.</p>

            <h2>2. Responsabilidade do Lojista</h2>
            <p>Os lojistas que utilizam a nossa plataforma são responsáveis por informar aos seus respectivos clientes que os dados e conversas gerados através do canal de WhatsApp integrado são processados por sistemas de Inteligência Artificial, com o objetivo exclusivo de organizar e realizar agendamentos.</p>

            <h2>3. Segurança e Armazenamento</h2>
            <p>A proteção da sua privacidade é nossa prioridade. Armazenamos e protegemos as informações em bancos de dados isolados e seguros. O conteúdo das mensagens e os dados dos clientes finais são utilizados unicamente para o propósito contratado e, em hipótese alguma, são comercializados, compartilhados ou cedidos a terceiros para outros fins.</p>

            <h2>4. Aceite dos Termos</h2>
            <p>Ao utilizar o nosso aplicativo e os nossos serviços de Inteligência Artificial, o lojista concorda expressamente com o processamento dos dados conforme estipulado nesta política e confirma estar ciente da sua responsabilidade perante a LGPD e demais legislações aplicáveis no uso da ferramenta.</p>
            
            <hr style="margin-top:40px; border: 0; border-top: 1px solid #ecf0f1;">
            <p style="font-size: 13px; color: #7f8c8d; text-align: center;">Última atualização: Junho de 2026</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# =========================================================
# WEBSOCKETS

@app.websocket("/ws/notificacoes")
async def websocket_notificacoes(websocket: WebSocket, token: str = Query(None)):
    if not token:
        await websocket.close(code=1008)
        return

    try:
        # Decodifica o token para descobrir qual loja está conectando
        payload = decodificar_token_jwt(token)
        schema = payload.get("schema")
        
        # O administrador pode estar atuando como outra loja
        acting_as = payload.get("acting_as")
        if acting_as:
            # Pra manter simples, nós mapearemos as conexões pelo "schema" associado
            # àquele codigo_loja na DB. Porém, para evitar consulta ao banco no WS,
            # usamos o próprio acting_as (codigo_loja) se ele existir, ou schema se não.
            # No caso do AdminSwitch, auth_service.py usa "acting_as" = codigo_loja.
            # Vou usar o schema original ou "sub_..." para fallbacks, ou buscar do DB.
            pass

    except Exception as e:
        logger.error(f"WebSocket Token Inválido: {e}")
        await websocket.close(code=1008)
        return

    # Usaremos o schema obtido do token. Se o usuário for lojista de verdade, o schema estará lá.
    if not schema:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, schema)
    try:
        while True:
            # O cliente pode enviar ping/pongs ou mensagens, mas não esperamos processar
            # comandos do cliente via WS. Apenas mantemos a conexão aberta.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, schema)
