import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:134001@localhost:5432/central_agendamento_db")
engine = create_engine(DATABASE_URL)

def run():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, nome_loja, nome_do_schema, numero_whatsapp FROM merchant")).fetchall()
        for r in res:
            print(f"ID: {r[0]} | Schema: {r[2]} | Loja: {r[1]} | WPP: {r[3]}")

if __name__ == "__main__":
    run()
