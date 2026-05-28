from app.database import engine
from sqlalchemy import text

def listar_merchants():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, nome_loja, codigo_loja, nome_do_schema FROM merchant")).mappings().fetchall()
        for row in result:
            print(dict(row))

if __name__ == "__main__":
    listar_merchants()
