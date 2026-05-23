from app.database import SessionLocal
from app.services.session_service import salvar_sessao_cliente, get_sessao_cliente

db = SessionLocal()
try:
    print("Tentando salvar sessão...")
    salvar_sessao_cliente(db, "554199692193", "moura_schema", {"teste": True})
    
    sessao = get_sessao_cliente(db, "554199692193")
    if sessao:
        print(f"Sessão salva com sucesso! Loja: {sessao.loja_atual}")
    else:
        print("Sessão não foi salva!")
except Exception as e:
    print(f"Erro: {e}")
finally:
    db.close()
