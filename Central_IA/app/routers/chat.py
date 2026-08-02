import logging
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.database import get_public_db
from app.models import Merchant
from app.models.chat import ClientChatState, ChatMessage
from app.services.auth_service import get_lojista_atual
from app.services.whatsapp_service import enviar_mensagem_whatsapp
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

from typing import cast

def _get_real_merchant_id(db: Session, lojista: Merchant) -> int:
    real = db.query(Merchant).filter(
        Merchant.nome_do_schema == lojista.nome_do_schema, 
        Merchant.loja_pai_id.is_(None)
    ).first()
    return cast(int, real.id if real else lojista.id)

router = APIRouter(
    prefix="/api/mobile/chat",
    tags=["Chat App Lojista"],
)

class SendMessageRequest(BaseModel):
    client_phone: str
    message: str

class EndServiceRequest(BaseModel):
    client_phone: str

@router.get("/clients")
def list_chat_sessions(
    db: Session = Depends(get_public_db),
    lojista: Merchant = Depends(get_lojista_atual)
):
    # Base query for all active human sessions
    sessions_query = db.query(ClientChatState).join(
        Merchant, ClientChatState.merchant_id == Merchant.id
    ).filter(
        ClientChatState.is_human_service == True
    )

    # Se for admin, vê todas as conversas de todos os lojistas, independente de qual schema está acessando.
    # Caso contrário (lojista comum), filtra rigidamente pelo seu próprio schema.
    if not getattr(lojista, 'is_admin', False):
        sessions_query = sessions_query.filter(Merchant.nome_do_schema == lojista.nome_do_schema)
        
    sessions = sessions_query.order_by(ClientChatState.human_service_started_at.desc()).all()
    
    dados = []
    for s in sessions:
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.merchant_id == s.merchant_id,
            ChatMessage.client_phone == s.client_phone
        ).order_by(ChatMessage.timestamp.desc()).first()
        
        unread_count = db.query(ChatMessage).filter(
            ChatMessage.merchant_id == s.merchant_id,
            ChatMessage.client_phone == s.client_phone,
            ChatMessage.sender == 'client',
            ChatMessage.read == False
        ).count()

        dados.append({
            "client_phone": s.client_phone,
            "client_name": s.client_name,
            "is_human_service": s.is_human_service,
            "human_service_started_at": s.human_service_started_at,
            "last_message": last_msg.message_content if last_msg else "Nenhuma mensagem",
            "last_message_at": last_msg.timestamp if last_msg else s.human_service_started_at,
            "unread_count": unread_count
        })

    return {"dados": dados}

def _get_merchant_id_for_chat(db: Session, lojista: Merchant, client_phone: str) -> int:
    query = db.query(ClientChatState).filter(ClientChatState.client_phone == client_phone)
    if not getattr(lojista, 'is_admin', False):
        query = query.join(Merchant).filter(Merchant.nome_do_schema == lojista.nome_do_schema)
    state = query.order_by(ClientChatState.human_service_started_at.desc()).first()
    if not state:
        raise HTTPException(status_code=404, detail="Histórico não encontrado.")
    return state.merchant_id

@router.get("/history/{client_phone}")
def get_chat_history(
    client_phone: str,
    db: Session = Depends(get_public_db),
    lojista: Merchant = Depends(get_lojista_atual)
):
    """Puxa o histórico de mensagens de um cliente específico."""
    merchant_id = _get_merchant_id_for_chat(db, lojista, client_phone)
    messages = db.query(ChatMessage).filter(
        ChatMessage.merchant_id == merchant_id,
        ChatMessage.client_phone == client_phone
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return {"dados": [
        {
            "id": m.id,
            "message_content": m.message_content,
            "sender": m.sender,
            "created_at": m.timestamp,
            "read": m.read
        } for m in messages
    ]}

@router.post("/send")
async def send_chat_message(
    req: SendMessageRequest,
    db: Session = Depends(get_public_db),
    lojista: Merchant = Depends(get_lojista_atual)
):
    """Lojista envia uma mensagem para o cliente pelo app."""
    merchant_id = _get_merchant_id_for_chat(db, lojista, req.client_phone)
    
    # 1. Salvar no banco
    msg = ChatMessage(
        merchant_id=merchant_id,
        client_phone=req.client_phone,
        message_content=req.message,
        sender="merchant"
    )
    db.add(msg)
    
    # 2. Atualizar estado de atendimento humano (Pausa o Bot)
    from datetime import datetime, timezone
    state = db.query(ClientChatState).filter(
        ClientChatState.merchant_id == merchant_id,
        ClientChatState.client_phone == req.client_phone
    ).first()
    
    if state:
        state.is_human_service = True
        state.human_service_started_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(msg)
    
    try:
        # Configurar as variáveis de contexto para usar o token correto da loja
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        from app.services.whatsapp_service import current_token, current_phone_id, current_merchant_id
        
        if merchant:
            current_merchant_id.set(merchant.id)
            if merchant.meta_access_token:
                current_token.set(merchant.meta_access_token)
            if merchant.meta_phone_id:
                current_phone_id.set(merchant.meta_phone_id)
            
        enviar_mensagem_whatsapp(
            numero_destino=req.client_phone,
            texto=req.message
        )
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem WhatsApp para {req.client_phone}: {e}")
    
    return {"status": "success", "message_id": msg.id}

@router.post("/end")
def end_human_service(
    req: EndServiceRequest,
    db: Session = Depends(get_public_db),
    lojista: Merchant = Depends(get_lojista_atual)
):
    """Encerra o atendimento humano e retorna o cliente para a IA."""
    merchant_id = _get_merchant_id_for_chat(db, lojista, req.client_phone)
    state = db.query(ClientChatState).filter(
        ClientChatState.merchant_id == merchant_id,
        ClientChatState.client_phone == req.client_phone
    ).first()
    
    if not state:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
    state.is_human_service = False
    db.commit()
    
    return {"status": "success", "message": "Atendimento humano encerrado. IA retomada."}
