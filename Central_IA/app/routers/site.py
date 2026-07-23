import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_public_db
from app.models.site_chat_log import SiteChatLog
from app.services.openai_service import responder_chat_site

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
async def process_chat_message(msg: SiteChatMessage, db: Session = Depends(get_public_db)):
    """Recebe a mensagem do usuário, salva, envia pro GPT e devolve a resposta."""
    try:
        if msg.remetente != 'user':
            raise HTTPException(status_code=400, detail="Apenas mensagens de user são permitidas neste endpoint.")
            
        # 1. Salva a mensagem do usuário
        log_user = SiteChatLog(
            session_id=msg.session_id,
            remetente='user',
            mensagem=msg.mensagem
        )
        db.add(log_user)
        db.commit()
        
        # 2. Busca histórico recente da mesma sessão (últimas 10 mensagens)
        historico_db = db.query(SiteChatLog).filter(SiteChatLog.session_id == msg.session_id).order_by(SiteChatLog.criado_em.desc()).limit(10).all()
        historico_db.reverse() # Mais antigas primeiro
        
        historico_para_ia = [
            {"remetente": h.remetente, "mensagem": h.mensagem}
            for h in historico_db if h.id != log_user.id
        ]
        
        # Filtra a última mensagem do histórico
        historico_limpo = historico_para_ia[:-1] if len(historico_para_ia) > 0 and historico_para_ia[-1]["mensagem"] == msg.mensagem else historico_para_ia

        # 3. Verifica se a mensagem bate com scripts locais para economizar tokens
        mensagem_lower = msg.mensagem.lower().strip()
        
        if mensagem_lower in ["oi", "oie", "olá", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem", "tudo bem?", "oi!"]:
            resposta_ia = {
                "mensagem": "Olá! Eu sou a Lau, assistente inteligente do OpenChaTz. 🤖✨\n\nEstou aqui para tirar todas as suas dúvidas sobre como automatizar seus agendamentos pelo WhatsApp. Como posso te ajudar hoje?",
                "isLink": False
            }
        elif mensagem_lower in ["preço", "preco", "qual o valor", "qual o valor?", "quanto custa", "quanto custa?", "valores", "planos"]:
            resposta_ia = {
                "mensagem": "Atualmente estamos com uma **promoção de lançamento por apenas R$ 57,00/mês!** (O preço oficial é R$ 87,00/mês).\n\nE o melhor: você pode testar o sistema **DE GRAÇA por 7 dias**, sem precisar cadastrar cartão de crédito!\n\nQuer saber como funciona o teste grátis?",
                "isLink": False
            }
        else:
            # Chama a IA de verdade
            resposta_ia = await responder_chat_site(historico_limpo, msg.mensagem)
        
        # 4. Salva a resposta da IA no banco
        log_bot = SiteChatLog(
            session_id=msg.session_id,
            remetente='bot',
            mensagem=resposta_ia["mensagem"]
        )
        db.add(log_bot)
        db.commit()
        
        # 5. Retorna
        return {
            "status": "success",
            "reply": resposta_ia["mensagem"],
            "isLink": resposta_ia["isLink"]
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar log de chat do site: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar mensagem")
