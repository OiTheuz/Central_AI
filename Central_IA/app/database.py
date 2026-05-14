from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

# =========================================================
# ENGINE & SESSION

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# =========================================================
# DEPENDENCY — usado nos routers via Depends()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# UTILITÁRIO — verificar disponibilidade de horário

def verificar_disponibilidade(schema_nome, data, hora, servico):
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', schema_nome):
        raise ValueError("Nome do schema contém caracteres inválidos.")

    db = SessionLocal()
    try:
        db.execute(text(f"SET search_path TO {schema_nome}"))

        query = text("""
            SELECT id FROM horarios_disponiveis 
            WHERE data = :data AND hora = :hora AND servico = :servico AND disponivel = TRUE
        """)

        resultado = db.execute(query, {"data": data, "hora": hora, "servico": servico}).fetchone()

        return resultado is not None
    finally:
        db.close()
