from app.database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE merchant ADD COLUMN foto_perfil VARCHAR(500) NULL;"))
        conn.commit()
    print("Success!")

if __name__ == "__main__":
    run()
