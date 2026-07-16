import os

whatsapp_file = r"c:\Users\MouTh\OneDrive\Área de Trabalho\Projeto Python\Central_IA\app\services\whatsapp_service.py"
with open(whatsapp_file, "a", encoding="utf-8") as f:
    f.write('''

def baixar_media_whatsapp(media_id: str, phone_number_id: str | None = None, token: str | None = None) -> bytes | None:
    """Baixa o arquivo binário da Meta"""
    TOKEN_META = get_token(token)
    PHONE_NUMBER_ID = get_phone_id(phone_number_id)
    if not TOKEN_META or not PHONE_NUMBER_ID:
        logger.error("Credenciais Meta ausentes — não foi possível baixar media_id %s", media_id)
        return None
    url_info = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {TOKEN_META}"}
    import requests
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
''')

openai_file = r"c:\Users\MouTh\OneDrive\Área de Trabalho\Projeto Python\Central_IA\app\services\openai_service.py"
with open(openai_file, "a", encoding="utf-8") as f:
    f.write('''

import tempfile
import os

async def transcrever_audio_com_ia(audio_bytes: bytes) -> str:
    """Usa Whisper para transcrever áudio"""
    if not audio_bytes: return ""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
    try:
        temp_file.write(audio_bytes)
        temp_file.close()
        with open(temp_file.name, 'rb') as audio_file:
            response = await client_ai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )
        return response.text.strip()
    except Exception as e:
        logger.error("Erro ao transcrever audio: %s", e)
        return ""
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
''')
