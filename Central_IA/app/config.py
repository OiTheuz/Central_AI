import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (na raiz do projeto)
load_dotenv()

# =========================================================
# HELPER — garante que variáveis obrigatórias existam

def _obter_env(chave: str) -> str:
    valor = os.getenv(chave)
    if valor is None:
        raise RuntimeError(f"⛔ Variável de ambiente '{chave}' não encontrada no .env!")
    return valor

# =========================================================
# BANCO DE DADOS
DATABASE_URL: str = _obter_env("DATABASE_URL")

# =========================================================
# OPENAI
OPENAI_API_KEY: str = _obter_env("OPENAI_API_KEY")

# =========================================================
# META / WHATSAPP
META_ACCESS_TOKEN: str = _obter_env("META_ACCESS_TOKEN")
META_PHONE_ID: str = _obter_env("META_PHONE_ID")
VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN_META", "AgendAI_Meta_9f2a8b3c7e5d10a4f6b2")
