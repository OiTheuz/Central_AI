from app.database import SessionLocal
from app.models.active_session import ActiveSession
import json

db = SessionLocal()
session = db.query(ActiveSession).filter(ActiveSession.telefone_cliente == '554199692193').first()
if session:
    print(f"Loja: {session.loja_atual}")
    print(f"Ativo: {session.ativo}")
    print(f"Dados: {json.dumps(session.dados_sessao, indent=2, ensure_ascii=False)}")
else:
    print("Nenhuma sessao encontrada.")
db.close()
