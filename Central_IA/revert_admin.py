from sqlalchemy import text
from app.database import engine

def revert_admin():
    with engine.connect() as conn:
        # Reverte apenas a loja pai "jessiely_moura"
        conn.execute(
            text("UPDATE merchant SET nome_loja = 'Jessiely Moura' WHERE nome_do_schema = 'jessiely_moura' AND loja_pai_id IS NULL")
        )
        
        # Se existir algum sub-usuário com email admin@lautz.tech, podemos mudar o nome dele para Matheus Moura
        conn.execute(
            text("UPDATE merchant SET nome_loja = 'Matheus Moura' WHERE email = 'admin@lautz.tech' AND loja_pai_id IS NOT NULL")
        )
        
        conn.commit()
        print("✅ Loja revertida para 'Jessiely Moura'!")

if __name__ == "__main__":
    revert_admin()
