import sys
import os

# Ensure the root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from sqlalchemy import text
from app.services.schema_service import listar_schemas

def update_db():
    with engine.connect() as conn:
        schemas = listar_schemas()
        for schema in schemas:
            try:
                print(f"Atualizando schema: {schema}")
                # Tentar adicionar a coluna data_nascimento na tabela customers
                conn.execute(text(f"ALTER TABLE {schema}.customers ADD COLUMN data_nascimento VARCHAR(20);"))
                conn.commit()
                print(f"Sucesso: Coluna 'data_nascimento' adicionada em {schema}.customers.")
            except Exception as e:
                # Pode já existir ou a tabela customers não existir
                if 'customers' not in str(e):
                    print(f"Aviso em {schema}: {e}")
                else:
                    print(f"Coluna possivelmente já existe ou tabela customers não existe em {schema}.")
                conn.rollback()

if __name__ == "__main__":
    update_db()
