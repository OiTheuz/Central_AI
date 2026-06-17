import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import get_public_db

def migrar():
    db = next(get_public_db())
    try:
        # Verifica se a coluna já existe
        col = db.execute(text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'merchant' AND column_name = 'nome_usuario'
        """)).fetchone()

        if not col:
            # Adiciona a coluna
            db.execute(text("ALTER TABLE merchant ADD COLUMN nome_usuario VARCHAR(255)"))
            print("✅ Coluna 'nome_usuario' adicionada com sucesso.")
            
            # Copia os dados existentes do nome_loja para o nome_usuario
            db.execute(text("UPDATE merchant SET nome_usuario = nome_loja"))
            
            # Ajusta especificamente a conta admin@lautz.tech
            db.execute(text("UPDATE merchant SET nome_usuario = 'Matheus Moura' WHERE email = 'admin@lautz.tech'"))
            print("✅ Dados populados.")
        else:
            print("~ Coluna 'nome_usuario' já existe.")
            # Garante que admin@lautz.tech está correto
            db.execute(text("UPDATE merchant SET nome_usuario = 'Matheus Moura' WHERE email = 'admin@lautz.tech'"))

        db.commit()
        print("🎉 Banco atualizado com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro na migração: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrar()
