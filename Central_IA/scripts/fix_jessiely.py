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

def fix_jessiely():
    with engine.begin() as conn:
        # Atualiza o numero da Jessiely para o correto em produção (com 55)
        conn.execute(
            text("UPDATE merchant SET numero_whatsapp = '5544991655311' WHERE nome_do_schema = 'jessiely_moura' OR nome_do_schema = 'moura'")
        )
        print("✅ Número da Jessiely (5544991655311) atualizado no banco com sucesso!")

if __name__ == "__main__":
    fix_jessiely()
