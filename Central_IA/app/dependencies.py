# ============================================================
# Dependencies centrais — get_db com schema do lojista
# ============================================================

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal, validar_schema
from app.models import Merchant
from app.services.auth_service import get_lojista_atual


import logging
logger = logging.getLogger(__name__)

def get_db(merchant: Merchant = Depends(get_lojista_atual)):
    """
    Dependency que retorna uma sessão já com o search_path
    configurado para o schema do lojista autenticado.
    Usado em todas as rotas protegidas por JWT.
    """
    db = SessionLocal()
    try:
        schema = validar_schema(str(merchant.nome_do_schema))
        logger.warning(f"DEBUG: get_db conectando ao schema -> {schema} para merchant {merchant.id} (loja_pai: {merchant.loja_pai_id})")
        db.execute(text(f"SET search_path TO {schema}, public"))
        yield db
    finally:
        try:
            db.execute(text("SET search_path TO public"))
            db.commit()
        except Exception:
            pass
        db.close()
