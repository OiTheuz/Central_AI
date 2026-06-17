from sqlalchemy import text
from app.database import engine

def fix_loja():
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE merchant SET nome_loja = 'Jessiely Moura' WHERE nome_do_schema = 'jessiely_moura'")
        )
        conn.commit()
        print("✅ Estabelecimento 'jessiely_moura' renomeado para 'Jessiely Moura' com sucesso!")

if __name__ == "__main__":
    fix_loja()
