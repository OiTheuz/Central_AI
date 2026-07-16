import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Merchant
from app.services.auth_service import decodificar_token_jwt
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws/chat",
    tags=["WebSockets Chat"],
)

@router.websocket("/")
async def chat_websocket(websocket: WebSocket, token: str = Query(...)):
    """
    Endpoint de WebSocket para o Lojista receber mensagens em tempo real.
    O App Lojista deve conectar em ws://.../ws/chat/?token=<JWT>
    """
    # Validar token
    try:
        payload = decodificar_token_jwt(token)
        lojista_id = payload.get("merchant_id")
        if not lojista_id:
            await websocket.close(code=1008, reason="Token inválido")
            return
            
        # Buscar loja no BD
        db = SessionLocal()
        try:
            lojista = db.query(Merchant).filter(Merchant.id == int(lojista_id)).first()
            if not lojista:
                await websocket.close(code=1008, reason="Lojista não encontrado")
                return
            schema_name = lojista.nome_do_schema
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao validar token do WebSocket: {e}")
        await websocket.close(code=1008, reason="Autenticação falhou")
        return

    # Conectar ao manager
    await manager.connect(websocket, schema_name)
    try:
        while True:
            # Mantém a conexão aberta aguardando mensagens (se o lojista enviar algo por WS)
            # Como nosso envio será via REST (POST /send), o WS serve apenas para RECERBER,
            # mas precisamos manter o loop recebendo ping/pong para não desconectar.
            data = await websocket.receive_text()
            # Opcional: Processar algo recebido
    except WebSocketDisconnect:
        manager.disconnect(websocket, schema_name)
