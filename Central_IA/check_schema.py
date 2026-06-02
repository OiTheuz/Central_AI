from app.database import engine
from sqlalchemy import text

def check():
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_namespace n ON n.oid = c.connamespace
            WHERE n.nspname = 'moura_schema' AND c.contype IN ('u', 'p')
        """))
        print("Constraints in moura_schema:")
        for r in res.fetchall():
            print(r)

if __name__ == "__main__":
    check()
