import sys
import os

# Adiciona o diretório atual ao path para importação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine

def add_push_token_column():
    print("Verificando estrutura da tabela merchant...")
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE merchant ADD COLUMN push_token VARCHAR(255)"))
            conn.commit()
            print("[OK] Coluna 'push_token' adicionada com sucesso a tabela merchant!")
    except Exception as e:
        if "already exists" in str(e).lower() or "já existe" in str(e).lower():
            print("[AVISO] A coluna 'push_token' ja existe na tabela merchant.")
        else:
            print(f"[ERRO] Erro ao alterar tabela: {e}")

if __name__ == "__main__":
    add_push_token_column()
