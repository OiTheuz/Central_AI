import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

env_file = Path(__file__).parent.parent / ".env"
if not env_file.exists():
    env_file = Path(__file__).parent / ".env"

if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrado no ambiente ou no .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def copy_meta_credentials():
    with engine.begin() as conn:
        # Busca a loja antiga (Moura)
        result = conn.execute(text("SELECT meta_access_token, meta_phone_id FROM merchant WHERE nome_do_schema = 'jessiely_moura' OR nome_do_schema = 'moura'")).fetchall()
        
        token = None
        phone_id = None
        
        for row in result:
            if row[0] and row[1]:
                token = row[0]
                phone_id = row[1]
                break
                
        if not token:
            print("Token antigo não encontrado na loja Moura. Usando variaveis de ambiente caso existam.")
            
        # Atualiza a loja Petshop
        conn.execute(
            text("UPDATE merchant SET meta_access_token = :t, meta_phone_id = :p WHERE area_atuacao = 'petshop' OR nome_do_schema LIKE '%pet%'"),
            {"t": token, "p": phone_id}
        )
        print("✅ Credenciais da Meta copiadas para o Petshop com sucesso!")

if __name__ == "__main__":
    copy_meta_credentials()
