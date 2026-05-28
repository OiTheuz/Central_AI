from app.database import engine
from sqlalchemy import text

def update_db():
    with engine.connect() as conn:
        try:
            # Tentar adicionar as colunas no schema public, tabela merchant
            conn.execute(text("ALTER TABLE merchant ADD COLUMN email VARCHAR(255) UNIQUE;"))
            conn.commit()
            print("Coluna 'email' adicionada.")
        except Exception as e:
            print(f"Coluna 'email' possivelmente já existe ou erro: {e}")
            
        try:
            conn.execute(text("ALTER TABLE merchant ADD COLUMN senha_hash VARCHAR(255);"))
            conn.commit()
            print("Coluna 'senha_hash' adicionada.")
        except Exception as e:
            print(f"Coluna 'senha_hash' possivelmente já existe ou erro: {e}")

if __name__ == "__main__":
    update_db()
