"""
Migration: Adiciona colunas de configuração de notificações na tabela merchant.

Execute na VPS:
    python3 add_notificacoes_merchant.py
"""
import os
import sys

# ─── Carrega DATABASE_URL direto do .env ──────────────────────
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

database_url = None
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL='):
                database_url = line.split('=', 1)[1].strip().strip('"').strip("'")
                break

if not database_url:
    database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL não encontrada.")
    sys.exit(1)

print(f"✅ DATABASE_URL encontrada.")

# ─── Conecta via psycopg2 ─────────────────────────
try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 não instalado.")
    sys.exit(1)

conn = psycopg2.connect(database_url)
conn.autocommit = False
cur = conn.cursor()

colunas_para_adicionar = [
    "notificacoes_push_enabled",
    "notificacoes_novos",
    "notificacoes_cancelamentos",
    "notificacoes_lembretes"
]

for coluna in colunas_para_adicionar:
    try:
        # Verifica se a coluna já existe
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'merchant'
              AND column_name = %s
        """, (coluna,))
        existe = cur.fetchone()

        if existe:
            print(f"  Coluna '{coluna}' já existe na tabela merchant. Pulando.")
        else:
            cur.execute(f"ALTER TABLE public.merchant ADD COLUMN {coluna} BOOLEAN NOT NULL DEFAULT TRUE")
            conn.commit()
            print(f"  ✅ Coluna '{coluna}' adicionada com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Erro ao adicionar '{coluna}': {e}")

cur.close()
conn.close()
print("\n✅ Migration da tabela merchant concluída!")
