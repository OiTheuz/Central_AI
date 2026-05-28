import logging
import re
import requests

logger = logging.getLogger(__name__)

_VALID_EXPO_TOKEN = re.compile(r'^ExponentPushToken\[.+\]$')

def enviar_notificacao_push(push_token: str, titulo: str, corpo: str, dados: dict | None = None) -> bool:
    """
    Envia uma notificação Push via API do Expo.
    :param push_token: O ExponentPushToken do dispositivo.
    :param titulo: Título da notificação.
    :param corpo: Mensagem principal da notificação.
    :param dados: JSON extra para processamento interno no app.
    :return: True se enviado com sucesso, False caso contrário.
    """
    if not push_token or not _VALID_EXPO_TOKEN.match(push_token):
        logger.warning("Push token inválido ou ausente, notificação não enviada.")
        return False
        
    url = "https://exp.host/--/api/v2/push/send"
    
    payload = {
        "to": push_token,
        "sound": "default",
        "title": titulo,
        "body": corpo,
        "data": dados or {}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            # A API Expo retorna status por token dentro de "data"
            ticket = result.get("data", {})
            if ticket.get("status") == "error":
                logger.error(
                    "Expo Push erro para token %s: %s",
                    push_token, ticket.get("message")
                )
                return False
            logger.info("Push notification enviada com sucesso para %s", push_token[:30])
            return True
        else:
            logger.error(
                "Expo Push HTTP %s: %s", response.status_code, response.text
            )
            return False
    except requests.Timeout:
        logger.error("Expo Push: timeout ao enviar notificação")
        return False
    except Exception as e:
        logger.error("Expo Push: falha de rede inesperada: %s", e)
        return False
