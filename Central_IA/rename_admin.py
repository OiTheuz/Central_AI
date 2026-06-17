from sqlalchemy import text
from app.database import engine

def rename_admin():
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE merchant SET nome_loja = 'Matheus Moura' WHERE nome_loja = 'Jessiely Moura'")
        )
        conn.commit()
        print("✅ Nome atualizado para Matheus Moura!")

if __name__ == "__main__":
    rename_admin()
