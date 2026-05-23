from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
r = db.execute(text("SELECT nome_loja FROM public.merchant"))
print(r.fetchall())
db.close()
