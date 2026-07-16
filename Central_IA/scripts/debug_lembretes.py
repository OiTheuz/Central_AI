import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text

env_file = Path("/var/www/central_ai/.env")
if not env_file.exists():
    print("Sem .env")
    sys.exit(1)

for line in env_file.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("=== DADOS DE AGENDAMENTO (GERAL) ===")
    res = conn.execute(text("SELECT nome_do_schema FROM merchant"))
    schemas = [r[0] for r in res.fetchall()]
    
    for schema in schemas:
        try:
            query = f"""
                SELECT 
                    a.id, a.data_agendamento, a.horario_agendamento, a.status, a.lembrete_pre_enviado,
                    c.telefone_whatsapp,
                    s.nome AS servico, s.lembrete_pre_ativo, s.lembrete_pre_valor_intervalo, s.lembrete_pre_tipo_intervalo
                FROM {schema}.appointments a
                JOIN {schema}.services s ON a.service_id = s.id
                JOIN {schema}.customers c ON a.customer_id = c.id
                ORDER BY a.id DESC LIMIT 2
            """
            agendamentos = conn.execute(text(query)).mappings().fetchall()
            if agendamentos:
                print(f"\nSCHEMA: {schema}")
                for ag in agendamentos:
                    print(dict(ag))
        except Exception as e:
            print(f"Erro no schema {schema}: {e}")
            conn.rollback()
