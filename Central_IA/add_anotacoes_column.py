"""
Migration: Adiciona a coluna 'anotacoes' na tabela customers de todos os schemas.
Execute este script no servidor com o ambiente virtual ativado:
    python add_anotacoes_column.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, get_all_schemas  # ajuste conforme necessário

def run():
    schemas_to_migrate = []

    # Tenta obter todos os schemas dinamicamente
    try:
        from app.database import engine
        with engine.connect() as conn:
            # Pega todos os schemas que possuem a tabela 'customers'
            rows = conn.execute(text("""
                SELECT table_schema
                FROM information_schema.tables
                WHERE table_name = 'customers'
                  AND table_schema NOT IN ('pg_catalog', 'information_schema', 'public')
                ORDER BY table_schema
            """)).fetchall()
            schemas_to_migrate = [r[0] for r in rows]
    except Exception as e:
        print(f"Erro ao listar schemas: {e}")
        sys.exit(1)

    if not schemas_to_migrate:
        print("Nenhum schema encontrado com a tabela 'customers'.")
        return

    print(f"Schemas encontrados: {schemas_to_migrate}")
    
    with engine.connect() as conn:
        for schema in schemas_to_migrate:
            try:
                # Verifica se a coluna já existe
                exists = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = :schema
                      AND table_name = 'customers'
                      AND column_name = 'anotacoes'
                """), {"schema": schema}).fetchone()

                if exists:
                    print(f"  [{schema}] Coluna 'anotacoes' já existe. Pulando.")
                else:
                    conn.execute(text(f'ALTER TABLE "{schema}".customers ADD COLUMN anotacoes TEXT'))
                    conn.commit()
                    print(f"  [{schema}] ✅ Coluna 'anotacoes' adicionada com sucesso!")
            except Exception as e:
                print(f"  [{schema}] ❌ Erro: {e}")
                conn.rollback()

    print("\nMigration concluída!")

if __name__ == "__main__":
    run()
