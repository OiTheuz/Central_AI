"""
Migração: Adicionar coluna motivo_cancelamento em appointments.

Execute uma única vez no servidor:
    python add_motivo_cancelamento.py

Colunas adicionadas em cada schema de lojista:
  - motivo_cancelamento  TEXT  — motivo informado pelo cliente ao cancelar
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import get_public_db


def migrar():
    db = next(get_public_db())
    try:
        db.execute(text("SET search_path TO public"))
        schemas = db.execute(
            text("SELECT nome_do_schema FROM merchant WHERE nome_do_schema IS NOT NULL ORDER BY id")
        ).fetchall()

        print(f"Encontrados {len(schemas)} schema(s) de lojistas.")

        for (schema_name,) in schemas:
            if not re.match(r'^[a-zA-Z0-9_]+$', schema_name):
                print(f"  [SKIP] Schema inválido: {schema_name!r}")
                continue

            print(f"\n  Migrando schema: {schema_name}")

            schema_exists = db.execute(
                text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :s"),
                {"s": schema_name}
            ).fetchone()

            if not schema_exists:
                print(f"    [SKIP] Schema não encontrado no banco.")
                continue

            table_exists = db.execute(
                text("""
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = :s AND table_name = 'appointments'
                """),
                {"s": schema_name}
            ).fetchone()

            if not table_exists:
                print(f"    [SKIP] Tabela appointments não encontrada.")
                continue

            # motivo_cancelamento
            col = db.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = :s AND table_name = 'appointments' AND column_name = 'motivo_cancelamento'
            """), {"s": schema_name}).fetchone()

            if not col:
                db.execute(text(f'ALTER TABLE "{schema_name}".appointments ADD COLUMN motivo_cancelamento TEXT'))
                print(f"    + Coluna motivo_cancelamento adicionada.")
            else:
                print(f"    ~ Coluna motivo_cancelamento já existe.")

        db.commit()
        print("\n✅ Migração concluída com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro durante migração: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrar()
