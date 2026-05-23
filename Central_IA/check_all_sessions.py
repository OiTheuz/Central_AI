from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
r = db.execute(text("SELECT * FROM public.active_sessions"))
rows = r.fetchall()
for row in rows:
    print(row)
db.close()
