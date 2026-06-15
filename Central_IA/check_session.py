import json
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    res = conn.execute(text("SELECT telefone_cliente, dados_sessao, loja_atual FROM public.active_sessions ORDER BY ultima_interacao DESC LIMIT 1")).mappings().fetchone()
    if res:
        print(f"Telefone: {res['telefone_cliente']}")
        print(f"Loja: {res['loja_atual']}")
        print(f"Dados: {json.dumps(res['dados_sessao'], indent=2, ensure_ascii=False)}")
