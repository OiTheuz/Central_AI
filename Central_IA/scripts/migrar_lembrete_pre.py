import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def run_migration():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT nome_do_schema FROM merchant"))
        schemas = [row[0] for row in res.fetchall()]
        
        # Ensure template schema is also upgraded if not in merchant table
        if "template_petshop" not in schemas:
            schemas.append("template_petshop")
            
        print(f"Iniciando migração de {len(schemas)} schemas...")
        
        for schema in schemas:
            print(f"Migrando schema: {schema}")
            try:
                # Add to services (both POS and PRE reminders)
                cols_services = [
                    "lembrete_ativo BOOLEAN DEFAULT FALSE",
                    "lembrete_valor_intervalo INTEGER DEFAULT 0",
                    "lembrete_tipo_intervalo VARCHAR(50) DEFAULT 'dias'",
                    "lembrete_prompt TEXT DEFAULT ''",
                    "lembrete_pre_ativo BOOLEAN DEFAULT FALSE",
                    "lembrete_pre_valor_intervalo INTEGER DEFAULT 1",
                    "lembrete_pre_tipo_intervalo VARCHAR(50) DEFAULT 'horas'",
                    "lembrete_pre_prompt TEXT DEFAULT ''"
                ]
                for col in cols_services:
                    try:
                        conn.execute(text(f"ALTER TABLE {schema}.services ADD COLUMN IF NOT EXISTS {col}"))
                    except Exception as inner_e:
                        print(f"Erro ao adicionar {col} em {schema}: {inner_e}")
                
                # Add to appointments
                cols_appointments = [
                    "lembrete_enviado BOOLEAN DEFAULT FALSE",
                    "lembrete_pre_enviado BOOLEAN DEFAULT FALSE"
                ]
                for col in cols_appointments:
                    try:
                        conn.execute(text(f"ALTER TABLE {schema}.appointments ADD COLUMN IF NOT EXISTS {col}"))
                    except Exception as inner_e:
                        print(f"Erro ao adicionar {col} em {schema}: {inner_e}")
                
                conn.commit()
                print(f" -> Sucesso no schema {schema}")
            except Exception as e:
                conn.rollback()
                print(f" -> Erro CRITICO no schema {schema}: {e}")
                print(f" -> Erro no schema {schema}: {e}")

if __name__ == "__main__":
    run_migration()
