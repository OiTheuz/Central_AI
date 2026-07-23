import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_public_db
from app.models.site_chat_log import SiteChatLog

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/site",
    tags=["Site"],
)

class SiteChatMessage(BaseModel):
    session_id: str
    remetente: str
    mensagem: str

@router.post("/chat")
def save_chat_message(msg: SiteChatMessage, db: Session = Depends(get_public_db)):
    """Salva uma mensagem do widget de chat do site."""
    try:
        if msg.remetente not in ['user', 'bot']:
            raise HTTPException(status_code=400, detail="Remetente inválido")
            
        log = SiteChatLog(
            session_id=msg.session_id,
            remetente=msg.remetente,
            mensagem=msg.mensagem
        )
        db.add(log)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Erro ao salvar log de chat do site: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar mensagem")
