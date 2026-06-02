import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
res = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'merchant'")).fetchall()
print([r[0] for r in res])
db.close()
