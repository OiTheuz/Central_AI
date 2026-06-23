import logging
import requests
import contextvars

from app.config import META_ACCESS_TOKEN, META_PHONE_ID

logger = logging.getLogger(__name__)

# Variável de contexto para armazenar o ID do telefone da requisição atual
current_phone_id: contextvars.ContextVar[str] = contextvars.ContextVar("current_phone_id", default="")

def get_phone_id(passed_id: str = None) -> str:
    if passed_id:
        return passed_id
    ctx_id = current_phone_id.get()
    if ctx_id:
        return ctx_id
    return META_PHONE_ID

# ── Versão da Graph API da Meta ──────────────────────────────
# Atualize aqui quando a Meta deprecar a versão atual.
# Última versão estável verificada: v21.0 (jan/2025)
GRAPH_API_VERSION = "v21.0"

# =========================================================
# ENVIAR MENSAGEM VIA WHATSAPP (API Meta)

def enviar_mensagem_whatsapp(numero_destino: str, texto: str, phone_number_id: str = None) -> dict | None:
    """
    Envia uma mensagem de texto via API do WhatsApp Business da Meta.
    Retorna o JSON de resposta da API ou None em caso de falha.
    """
    TOKEN_META = META_ACCESS_TOKEN
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
        return response.json()
    except requests.Timeout:
        logger.error("WhatsApp: timeout ao enviar para %s", numero_destino)
        return None
    except Exception as e:
        logger.error("WhatsApp: falha inesperada ao enviar para %s: %s", numero_destino, e)
        return None

def enviar_menu_lojas_whatsapp(numero_destino: str, texto: str, lojas: list, phone_number_id: str = None) -> dict | None:
    """
    Envia uma mensagem interativa de lista com as lojas disponíveis.
    """
    TOKEN_META = META_ACCESS_TOKEN
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
        return response.json()
    except Exception as e:
        logger.error("WhatsApp: falha ao enviar menu para %s: %s", numero_destino, e)
        return None

def enviar_menu_intencao_whatsapp(numero_destino: str, texto: str, phone_number_id: str = None) -> dict | None:
    """
    Envia uma mensagem interativa perguntando a intenção do cliente:
    Agendar ou Consultar Status.
    """
    TOKEN_META = META_ACCESS_TOKEN
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)

    if not TOKEN_META or not PHONE_NUMBER_ID:
        logger.error("Credenciais Meta ausentes — menu não enviado para %s", numero_destino)
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Atendimento Lau 🤖"
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
        return response.json()
    except Exception as e:
        logger.error("WhatsApp: falha ao enviar menu intenção para %s: %s", numero_destino, e)
        return None

def enviar_menu_servicos_whatsapp(numero_destino: str, texto: str, servicos: list, phone_number_id: str = None) -> dict | None:
    """
    Envia uma mensagem interativa de lista com os serviços disponíveis.
    """
    TOKEN_META = META_ACCESS_TOKEN
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
        return response.json()
    except Exception as e:
        logger.error("WhatsApp: falha ao enviar menu de serviços para %s: %s", numero_destino, e)
        return None
