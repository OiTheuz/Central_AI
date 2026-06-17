from sqlalchemy import text
from app.database import engine

def revert():
    with engine.connect() as conn:
        conn.execute(text("UPDATE merchant SET nome_loja = 'Jessiely Moura' WHERE email = 'admin@lautz.tech'"))
        conn.commit()
        print("✅ Revertido! A conta admin@lautz.tech agora tem o nome de loja 'Jessiely Moura'.")

if __name__ == "__main__":
    revert()
