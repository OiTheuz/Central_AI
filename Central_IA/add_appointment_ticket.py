"""
Migração: Adicionar colunas de ticket e tipo de pendência em appointments.

Execute uma única vez no servidor:
    python add_appointment_ticket.py

Colunas adicionadas em cada schema de lojista:
  - numero_ticket       INTEGER  — número sequencial por loja (ex: ticket #1, #2...)
  - tipo_pendencia      VARCHAR  — NULL (normal) | 'cancelamento' | 'reagendamento'
  - reagendamento_data  DATE     — nova data solicitada pelo cliente (só para reagendamento)
  - reagendamento_hora  TIME     — novo horário solicitado pelo cliente (só para reagendamento)
"""

import sys
import os

# Adiciona o diretório raiz ao path para importar app.database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import get_public_db

def migrar():
    db = next(get_public_db())
    try:
        # 1. Busca todos os schemas de lojistas
        db.execute(text("SET search_path TO public"))
        schemas = db.execute(
            text("SELECT nome_do_schema FROM merchant WHERE nome_do_schema IS NOT NULL ORDER BY id")
        ).fetchall()

        print(f"Encontrados {len(schemas)} schema(s) de lojistas.")

        for (schema_name,) in schemas:
            # Sanitização básica do schema name (só letras, números e _)
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', schema_name):
                print(f"  [SKIP] Schema inválido/suspeito: {schema_name!r}")
                continue

            print(f"\n  Migrando schema: {schema_name}")

            # Verifica se o schema existe no banco
            schema_exists = db.execute(
                text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :s"),
                {"s": schema_name}
            ).fetchone()

            if not schema_exists:
                print(f"    [SKIP] Schema não encontrado no banco.")
                continue

            # Verifica se a tabela appointments existe no schema
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

            # ── 2. Adicionar colunas (se não existirem) ──

            # numero_ticket
            col_ticket = db.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = :s AND table_name = 'appointments' AND column_name = 'numero_ticket'
            """), {"s": schema_name}).fetchone()

            if not col_ticket:
                db.execute(text(f'ALTER TABLE "{schema_name}".appointments ADD COLUMN numero_ticket INTEGER'))
                print(f"    + Coluna numero_ticket adicionada.")
            else:
                print(f"    ~ Coluna numero_ticket já existe.")

            # tipo_pendencia
            col_tipo = db.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = :s AND table_name = 'appointments' AND column_name = 'tipo_pendencia'
            """), {"s": schema_name}).fetchone()

            if not col_tipo:
                db.execute(text(f'ALTER TABLE "{schema_name}".appointments ADD COLUMN tipo_pendencia VARCHAR(20)'))
                print(f"    + Coluna tipo_pendencia adicionada.")
            else:
                print(f"    ~ Coluna tipo_pendencia já existe.")

            # reagendamento_data
            col_reag_data = db.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = :s AND table_name = 'appointments' AND column_name = 'reagendamento_data'
            """), {"s": schema_name}).fetchone()

            if not col_reag_data:
                db.execute(text(f'ALTER TABLE "{schema_name}".appointments ADD COLUMN reagendamento_data DATE'))
                print(f"    + Coluna reagendamento_data adicionada.")
            else:
                print(f"    ~ Coluna reagendamento_data já existe.")

            # reagendamento_hora
            col_reag_hora = db.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = :s AND table_name = 'appointments' AND column_name = 'reagendamento_hora'
            """), {"s": schema_name}).fetchone()

            if not col_reag_hora:
                db.execute(text(f'ALTER TABLE "{schema_name}".appointments ADD COLUMN reagendamento_hora TIME'))
                print(f"    + Coluna reagendamento_hora adicionada.")
            else:
                print(f"    ~ Coluna reagendamento_hora já existe.")

            # ── 3. Popular numero_ticket nos registros existentes que ainda não têm ──
            db.execute(text(f"""
                UPDATE "{schema_name}".appointments
                SET numero_ticket = sub.rn
                FROM (
                    SELECT id, ROW_NUMBER() OVER (ORDER BY data_agendamento ASC NULLS LAST, horario_agendamento ASC NULLS LAST, id ASC) AS rn
                    FROM "{schema_name}".appointments
                    WHERE numero_ticket IS NULL
                ) sub
                WHERE "{schema_name}".appointments.id = sub.id
            """))

            registros_atualizados = db.execute(
                text(f'SELECT COUNT(*) FROM "{schema_name}".appointments WHERE numero_ticket IS NOT NULL')
            ).scalar()
            print(f"    ✓ {registros_atualizados} registro(s) com numero_ticket preenchido.")

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
