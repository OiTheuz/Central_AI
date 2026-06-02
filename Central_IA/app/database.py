import re
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

# =========================================================
# ENGINE & SESSION
# Pool configurado para produção com múltiplos workers
# =========================================================

engine = create_engine(
    DATABASE_URL,
    pool_size=10,         # conexões mantidas permanentemente
    max_overflow=20,      # conexões extras sob pico
    pool_pre_ping=True,   # verifica conexão antes de usar (evita broken pipe)
    pool_recycle=1800,    # recicla conexões a cada 30 min
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# =========================================================
# DEPENDENCY PÚBLICA — sessão sem schema (usado em login, webhook, etc.)
# =========================================================

def get_public_db():
    """Retorna uma sessão com search_path = public (sem schema de lojista)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.execute(text("SET search_path TO public"))
            db.commit()
        except Exception:
            pass
        db.close()

# =========================================================
# UTILITÁRIO — validação de schema name (anti SQL Injection)
# Reutilizável em qualquer router que faça SET search_path
# =========================================================

_SCHEMA_REGEX = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

def validar_schema(schema_nome: str) -> str:
    """
    Valida que o nome do schema contém apenas caracteres seguros
    (letras, números e underscore) para evitar SQL Injection.
    Levanta ValueError se inválido, retorna o schema se válido.
    """
    if not _SCHEMA_REGEX.match(schema_nome):
        logger.error("Schema inválido bloqueado: %s", schema_nome)
        raise ValueError(f"Nome do schema inválido: '{schema_nome}'")
    return schema_nome
