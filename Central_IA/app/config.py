import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (na raiz do projeto)
load_dotenv()

# =========================================================
# BANCO DE DADOS
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================================
# OPENAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =========================================================
# META / WHATSAPP
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_ID = os.getenv("META_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN_META", "AgendAI_Meta_9f2a8b3c7e5d10a4f6b2")
