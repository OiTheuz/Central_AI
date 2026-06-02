from app.database import engine
from sqlalchemy import text

def check():
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT column_name, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_schema = 'moura_schema' AND table_name = 'appointments'
        """))
        for r in res.fetchall():
            print(r)

if __name__ == "__main__":
    check()
