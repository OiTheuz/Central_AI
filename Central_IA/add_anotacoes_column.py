"""
Migration: Adiciona a coluna 'anotacoes' na tabela customers de todos os schemas.

Execute na VPS de dentro de /var/www/central_ai/Central_IA com venv ativo:
    cd /var/www/central_ai/Central_IA
    python3 add_anotacoes_column.py
"""
import os
import sys

# ─── Carrega DATABASE_URL direto do .env ──────────────────────
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    # Tenta um nível acima (caso rode de fora da pasta)
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
    print("❌ DATABASE_URL não encontrada no .env nem nas variáveis de ambiente.")
    sys.exit(1)

print(f"✅ DATABASE_URL encontrada.")

# ─── Conecta via psycopg2 diretamente ─────────────────────────
try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 não instalado. Rode: pip install psycopg2-binary")
    sys.exit(1)

conn = psycopg2.connect(database_url)
conn.autocommit = False
cur = conn.cursor()

# ─── Busca todos os schemas que têm a tabela customers ────────
cur.execute("""
    SELECT table_schema
    FROM information_schema.tables
    WHERE table_name = 'customers'
      AND table_schema NOT IN ('pg_catalog', 'information_schema', 'public')
    ORDER BY table_schema
""")
schemas = [row[0] for row in cur.fetchall()]

if not schemas:
    print("Nenhum schema encontrado com a tabela 'customers'.")
    cur.close()
    conn.close()
    sys.exit(0)

print(f"Schemas encontrados: {schemas}\n")

# ─── Adiciona a coluna em cada schema ─────────────────────────
for schema in schemas:
    try:
        # Verifica se já existe
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = 'customers'
              AND column_name = 'anotacoes'
        """, (schema,))
        existe = cur.fetchone()

        if existe:
            print(f"  [{schema}] Coluna 'anotacoes' já existe. Pulando.")
        else:
            cur.execute(f'ALTER TABLE "{schema}".customers ADD COLUMN anotacoes TEXT')
            conn.commit()
            print(f"  [{schema}] ✅ Coluna 'anotacoes' adicionada com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"  [{schema}] ❌ Erro: {e}")

cur.close()
conn.close()
print("\n✅ Migration concluída!")
