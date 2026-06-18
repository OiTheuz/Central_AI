"""
Script de migração: Remove constraints UNIQUE de nome_loja e numero_whatsapp
da tabela merchant, que bloqueiam a criação de sub-usuários.

Execute UMA VEZ na VPS:
  /var/www/central_ai/venv/bin/python fix_merchant_constraints.py
"""
import os
import sys

# Carrega as variáveis de ambiente do .env na pasta do script
from pathlib import Path
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import sqlalchemy as sa

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrado no ambiente ou no .env")
    sys.exit(1)

engine = sa.create_engine(DATABASE_URL)

fixes = [
    # Remover unique de nome_loja
    {
        "check": """
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_name = 'merchant'
              AND constraint_type = 'UNIQUE'
              AND constraint_name = 'merchant_nome_loja_key'
        """,
        "drop": "ALTER TABLE merchant DROP CONSTRAINT IF EXISTS merchant_nome_loja_key",
        "label": "UNIQUE(nome_loja)",
    },
    # Remover unique de numero_whatsapp
    {
        "check": """
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_name = 'merchant'
              AND constraint_type = 'UNIQUE'
              AND constraint_name = 'merchant_numero_whatsapp_key'
        """,
        "drop": "ALTER TABLE merchant DROP CONSTRAINT IF EXISTS merchant_numero_whatsapp_key",
        "label": "UNIQUE(numero_whatsapp)",
    },
]

with engine.connect() as conn:
    for fix in fixes:
        result = conn.execute(sa.text(fix["check"])).fetchone()
        if result:
            conn.execute(sa.text(fix["drop"]))
            conn.commit()
            print(f"✅ Constraint {fix['label']} removida com sucesso.")
        else:
            print(f"ℹ️  Constraint {fix['label']} não encontrada (já foi removida ou nome diferente).")

    # Verificar todos os constraints únicos restantes na tabela merchant
    print("\n📋 Constraints UNIQUE restantes na tabela merchant:")
    result = conn.execute(sa.text("""
        SELECT constraint_name FROM information_schema.table_constraints
        WHERE table_name = 'merchant' AND constraint_type = 'UNIQUE'
        ORDER BY constraint_name
    """)).fetchall()
    for row in result:
        print(f"  - {row[0]}")

print("\n🎉 Migração concluída!")
