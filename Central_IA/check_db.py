from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='moura_schema' AND table_name='customers'")).fetchall()
    print(res)
