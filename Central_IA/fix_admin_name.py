from sqlalchemy import text
from app.database import engine

def debug_and_fix():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, nome_loja, email, nome_do_schema, loja_pai_id, is_admin FROM merchant")).fetchall()
        print("=== TODAS AS CONTAS MERCHANT ===")
        for r in res:
            print(dict(r._mapping))
            
        # Tenta atualizar o super admin
        conn.execute(text("UPDATE merchant SET nome_loja = 'Matheus Moura' WHERE email = 'admin@lautz.tech'"))
        
        # Garante que a loja pai da Jessiely Moura continue como Jessiely Moura
        conn.execute(text("UPDATE merchant SET nome_loja = 'Jessiely Moura' WHERE nome_do_schema = 'jessiely_moura' AND email != 'admin@lautz.tech' AND loja_pai_id IS NULL"))
        
        conn.commit()

if __name__ == "__main__":
    debug_and_fix()
