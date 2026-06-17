from sqlalchemy import text
from app.database import engine

def debug_merchants():
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT id, nome_loja, codigo_loja, nome_do_schema, loja_pai_id
            FROM merchant
        """)).fetchall()
        
        print("=== TABELA MERCHANT ===")
        for r in res:
            print(r)

if __name__ == "__main__":
    debug_merchants()
