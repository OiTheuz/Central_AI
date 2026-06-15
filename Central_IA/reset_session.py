from app.database import engine
from sqlalchemy import text

telefone = "556198770803"

with engine.connect() as conn:
    with conn.begin():
        conn.execute(text(
            "UPDATE public.active_sessions SET ativo = FALSE WHERE telefone_cliente = :tel AND ativo = TRUE"
        ), {"tel": telefone})
    
    res = conn.execute(text(
        "SELECT telefone_cliente, ativo, dados_sessao FROM public.active_sessions WHERE telefone_cliente = :tel ORDER BY ultima_interacao DESC LIMIT 1"
    ), {"tel": telefone}).mappings().fetchone()
    
    if res:
        print(f"Telefone: {res['telefone_cliente']}")
        print(f"Ativo agora: {res['ativo']}")
        print(f"Dados: {res['dados_sessao']}")
    print("Sessão encerrada com sucesso!")
