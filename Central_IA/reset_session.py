from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text("DELETE FROM public.active_sessions WHERE telefone_cliente = '554199692193'"))
db.commit()
print("Sessao resetada com sucesso!")
db.close()
