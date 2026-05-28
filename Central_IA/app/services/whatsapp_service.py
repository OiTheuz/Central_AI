import logging
import requests

from app.config import META_ACCESS_TOKEN, META_PHONE_ID

logger = logging.getLogger(__name__)

# ── Versão da Graph API da Meta ──────────────────────────────
# Atualize aqui quando a Meta deprecar a versão atual.
# Última versão estável verificada: v21.0 (jan/2025)
GRAPH_API_VERSION = "v21.0"

# =========================================================
# ENVIAR MENSAGEM VIA WHATSAPP (API Meta)

def enviar_mensagem_whatsapp(numero_destino: str, texto: str) -> dict | None:
    """
    Envia uma mensagem de texto via API do WhatsApp Business da Meta.
    Retorna o JSON de resposta da API ou None em caso de falha.
    """
    TOKEN_META = META_ACCESS_TOKEN
    PHONE_NUMBER_ID = META_PHONE_ID

    if not TOKEN_META or not PHONE_NUMBER_ID:
        logger.error(
            "TOKEN_META ou PHONE_NUMBER_ID não configurados no .env — "
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
            "WhatsApp → %s | status=%s",
            numero_destino, response.status_code
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
