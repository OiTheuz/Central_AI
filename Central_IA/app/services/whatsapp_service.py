import requests

from app.config import META_ACCESS_TOKEN, META_PHONE_ID

# =========================================================
# ENVIAR MENSAGEM VIA WHATSAPP (API Meta)

def enviar_mensagem_whatsapp(numero_destino: str, texto: str):
    TOKEN_META = META_ACCESS_TOKEN
    PHONE_NUMBER_ID = META_PHONE_ID

    # Prevenção: Avisa no terminal se você esquecer de preencher o .env
    if not TOKEN_META or not PHONE_NUMBER_ID:
        print("❌ ERRO: TOKEN_META ou PHONE_NUMBER_ID não estão configurados no ficheiro .env!")
        return

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

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
        response = requests.post(url, headers=headers, json=data)
        print(f"↗️ Status do Envio: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

    return response.json()
