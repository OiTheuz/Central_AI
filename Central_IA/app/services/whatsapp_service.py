import logging
import requests
import contextvars
import re

from app.config import META_ACCESS_TOKEN, META_PHONE_ID

def sanitizar_numero_whatsapp(numero: str) -> str:
    """Remove caracteres especiais e garante o DDI 55 para números do Brasil com 10 ou 11 dígitos."""
    if not numero:
        return ""
    limpo = re.sub(r'\D', '', numero)
    if not limpo:
        return ""
    if len(limpo) in (10, 11):
        return f"55{limpo}"
    return limpo


logger = logging.getLogger(__name__)

# Variáveis de contexto para armazenar as credenciais do lojista da requisição atual
current_phone_id: contextvars.ContextVar[str] = contextvars.ContextVar("current_phone_id", default="")
current_token: contextvars.ContextVar[str] = contextvars.ContextVar("current_token", default="")
current_merchant_id: contextvars.ContextVar[int | None] = contextvars.ContextVar("current_merchant_id", default=None)

def _log_message(recipient: str, msg_type: str = "service"):
    merchant_id = current_merchant_id.get()
    if not merchant_id:
        return
    try:
        from app.database import SessionLocal
        from app.models.whatsapp_log import WhatsappMessageLog
        from datetime import datetime, timedelta, timezone
        
        with SessionLocal() as db:
            # A Meta cobra por CONVERSA (janela de 24 horas), e não por cada mensagem solta.
            # Vamos checar se já iniciamos uma conversa tarifada com este cliente nas últimas 24h.
            limite_24h = datetime.now(timezone.utc) - timedelta(hours=24)
            
            conversa_ativa = db.query(WhatsappMessageLog).filter(
                WhatsappMessageLog.merchant_id == merchant_id,
                WhatsappMessageLog.recipient == recipient,
                WhatsappMessageLog.message_type == msg_type,
                WhatsappMessageLog.sent_at >= limite_24h,
                WhatsappMessageLog.cost_estimated > 0 # Apenas procuramos a mensagem que abriu a cobrança
            ).first()
            
            # Se já tem uma conversa ativa, o custo dessa mensagem é zero!
            if conversa_ativa:
                cost = 0.0
            else:
                cost = 0.15 if msg_type == "service" else 0.17
                
            log = WhatsappMessageLog(merchant_id=merchant_id, recipient=recipient, message_type=msg_type, cost_estimated=cost)
            db.add(log)
            db.commit()
    except Exception as e:
        logger.error(f"Erro ao logar mensagem do whatsapp: {e}")

def get_phone_id(passed_id: str | None = None) -> str:
    if passed_id:
        return passed_id
    ctx_id = current_phone_id.get()
    if ctx_id:
        return ctx_id
    return META_PHONE_ID

def get_token(passed_token: str | None = None) -> str:
    if passed_token:
        return passed_token
    ctx_token = current_token.get()
    if ctx_token:
        return ctx_token
    return META_ACCESS_TOKEN

# ── Versão da Graph API da Meta ──────────────────────────────
# Atualize aqui quando a Meta deprecar a versão atual.
# Última versão estável verificada: v21.0 (jan/2025)
GRAPH_API_VERSION = "v21.0"

# =========================================================
# ENVIAR MENSAGEM VIA WHATSAPP (API Meta)

def enviar_mensagem_whatsapp(numero_destino: str, texto: str, phone_number_id: str | None = None, token: str | None = None) -> dict | None:
    """
    Envia uma mensagem de texto via API do WhatsApp Business da Meta.
    Retorna o JSON de resposta da API ou None em caso de falha.
    """
    numero_destino = sanitizar_numero_whatsapp(numero_destino)
    if not numero_destino:
        return None

    TOKEN_META = get_token(token)
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)

    if not TOKEN_META or not PHONE_NUMBER_ID:
        logger.error(
            "TOKEN_META ou PHONE_NUMBER_ID não configurados — "
            "mensagem para %s não enviada.", numero_destino
        )
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto}
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        logger.info(
            "WhatsApp → %s | status=%s (Phone ID: %s)",
            numero_destino, response.status_code, PHONE_NUMBER_ID
        )
        if not response.ok:
            logger.warning("WhatsApp API erro: %s", response.text)
        else:
            _log_message(numero_destino, "service")
        return response.json()
    except requests.Timeout:
        logger.error("WhatsApp: timeout ao enviar para %s", numero_destino)
        return None
    except Exception as e:
        logger.error("WhatsApp: falha inesperada ao enviar para %s: %s", numero_destino, e)
        return None

def enviar_botoes_whatsapp(numero_destino: str, texto: str, botoes: list[dict], phone_number_id: str | None = None, token: str | None = None) -> dict | None:
    """
    Envia uma mensagem com botões interativos (máx 3 botões).
    botoes deve ser uma lista de dicts no formato: [{"id": "id1", "title": "Sim"}, {"id": "id2", "title": "Não"}]
    """
    numero_destino = sanitizar_numero_whatsapp(numero_destino)
    if not numero_destino:
        return None

    TOKEN_META = get_token(token)
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)

    if not TOKEN_META or not PHONE_NUMBER_ID:
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }

    formatted_buttons = []
    for btn in botoes[:3]:
        formatted_buttons.append({
            "type": "reply",
            "reply": {
                "id": btn["id"],
                "title": btn["title"][:20] # Max 20 chars
            }
        })

    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": texto
            },
            "action": {
                "buttons": formatted_buttons
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        logger.info("WhatsApp (Botões) → %s | status=%s", numero_destino, response.status_code)
        if not response.ok:
            logger.warning("WhatsApp API erro (Botões): %s", response.text)
        else:
            _log_message(numero_destino, "service")
        return response.json()
    except Exception as e:
        logger.error("WhatsApp: falha ao enviar botões para %s: %s", numero_destino, e)
        return None

def enviar_menu_lojas_whatsapp(numero_destino: str, texto: str, lojas: list, phone_number_id: str | None = None) -> dict | None:
    """
    Envia uma mensagem interativa de lista com as lojas disponíveis.
    """
    TOKEN_META = get_token()
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)

    if not TOKEN_META or not PHONE_NUMBER_ID:
        logger.error("Credenciais Meta ausentes — menu não enviado para %s", numero_destino)
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }

    # Limite do WhatsApp: máximo de 10 opções por seção.
    rows = []
    for loja in lojas[:10]:
        nome = loja.nome_loja[:24] if loja.nome_loja else "Loja"
        desc = loja.area_atuacao[:72] if getattr(loja, 'area_atuacao', None) else "Agendamento online"
        rows.append({
            "id": f"LOJA_{loja.codigo_loja}",
            "title": nome,
            "description": desc
        })

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Lojas Disponíveis"
            },
            "body": {
                "text": texto
            },
            "footer": {
                "text": "Toque no botão para escolher"
            },
            "action": {
                "button": "Ver Lojas",
                "sections": [
                    {
                        "title": "Escolha o local",
                        "rows": rows
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        logger.info("WhatsApp (Menu) → %s | status=%s", numero_destino, response.status_code)
        if not response.ok:
            logger.warning("WhatsApp API erro (Menu): %s", response.text)
        else:
            _log_message(numero_destino, "service")
        return response.json()
    except Exception as e:
        logger.error("WhatsApp: falha ao enviar menu para %s: %s", numero_destino, e)
        return None

def enviar_menu_intencao_whatsapp(numero_destino: str, texto: str, phone_number_id: str | None = None, nome_loja: str = "Central") -> dict | None:
    """
    Envia uma mensagem interativa perguntando a intenção do cliente:
    Agendar ou Consultar Status.
    """
    TOKEN_META = get_token()
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)

    if not TOKEN_META or not PHONE_NUMBER_ID:
        logger.error("Credenciais Meta ausentes — menu não enviado para %s", numero_destino)
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }

    titulo_header = f"Atendimento {nome_loja} ✨"

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": titulo_header[:60]  # Limite da Meta é 60 chars
            },
            "body": {
                "text": texto
            },
            "footer": {
                "text": "Toque no botão para escolher"
            },
            "action": {
                "button": "Ver Opções",
                "sections": [
                    {
                        "title": "Como posso te ajudar?",
                        "rows": [
                            {
                                "id": "INTENT_AGENDAR",
                                "title": "Realizar Agendamento",
                                "description": "Marcar um novo horário"
                            },
                            {
                                "id": "INTENT_CONSULTAR",
                                "title": "Consultar Status",
                                "description": "Ver meus agendamentos"
                            }
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        logger.info("WhatsApp (Menu Intenção) → %s | status=%s (Phone ID: %s)", numero_destino, response.status_code, PHONE_NUMBER_ID)
        if not response.ok:
            logger.warning("WhatsApp API erro (Menu Intenção): %s", response.text)
        else:
            _log_message(numero_destino, "service")
        return response.json()
    except Exception as e:
        logger.error("WhatsApp: falha ao enviar menu intenção para %s: %s", numero_destino, e)
        return None

def enviar_menu_servicos_whatsapp(numero_destino: str, texto: str, servicos: list, phone_number_id: str | None = None) -> dict | None:
    """
    Envia uma mensagem interativa de lista com os serviços disponíveis.
    """
    TOKEN_META = get_token()
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)

    if not TOKEN_META or not PHONE_NUMBER_ID:
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }

    rows = []
    for servico in servicos[:10]:
        nome = servico.nome[:24]
        preco_formatado = f"R$ {servico.preco:.2f}" if servico.preco else ""
        desc = f"{servico.duracao} min" + (f" - {preco_formatado}" if preco_formatado else "")
        rows.append({
            "id": f"SERVICO_{servico.id}",
            "title": nome,
            "description": desc[:72]
        })

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Serviços Disponíveis"
            },
            "body": {
                "text": texto
            },
            "footer": {
                "text": "Toque no botão para escolher"
            },
            "action": {
                "button": "Ver Serviços",
                "sections": [
                    {
                        "title": "Selecione o serviço",
                        "rows": rows
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        logger.info("WhatsApp (Menu Serviços) → %s | status=%s (Phone ID: %s)", numero_destino, response.status_code, PHONE_NUMBER_ID)
        if not response.ok:
            logger.warning("WhatsApp API erro (Menu Serviços): %s", response.text)
        else:
            _log_message(numero_destino, "service")
        return response.json()
    except Exception as e:
        logger.error("WhatsApp: falha ao enviar menu de serviços para %s: %s", numero_destino, e)
        return None

def baixar_media_whatsapp(media_id: str, phone_number_id: str | None = None, token: str | None = None) -> bytes | None:
    """Baixa o arquivo binário da Meta"""
    TOKEN_META = get_token(token)
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)
    if not TOKEN_META or not PHONE_NUMBER_ID:
        logger.error("Credenciais Meta ausentes — não foi possível baixar media_id %s", media_id)
        return None
    url_info = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {TOKEN_META}"}
    try:
        resp_info = requests.get(url_info, headers=headers, timeout=10)
        if not resp_info.ok:
            logger.error("WhatsApp API erro URL media: %s", resp_info.text)
            return None
        media_url = resp_info.json().get("url")
        if not media_url: return None
        resp_media = requests.get(media_url, headers=headers, timeout=20)
        if not resp_media.ok: return None
        return resp_media.content
    except Exception as e:
        logger.error("Falha ao baixar media %s: %s", media_id, e)
        return None
