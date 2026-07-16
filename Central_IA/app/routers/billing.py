from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict
from app.database import get_public_db
from app.models.merchant import Merchant

router = APIRouter(
    prefix="/billing",
    tags=["billing"]
)

@router.post("/webhook/asaas")
async def asaas_webhook(request: Request, db: Session = Depends(get_public_db)):
    """
    Webhook para receber eventos do Asaas.
    Documentação: https://docs.asaas.com/docs/webhook-para-cobrancas
    """
    try:
        body = await request.json()
        
        # O Asaas envia um campo 'event' (ex: PAYMENT_RECEIVED, PAYMENT_OVERDUE)
        evento = body.get('event')
        pagamento = body.get('payment', {})
        
        asaas_customer_id = pagamento.get('customer')
        
        if not asaas_customer_id:
            return {"status": "ignorado", "motivo": "Sem customer_id"}
            
        merchant = db.query(Merchant).filter(Merchant.asaas_customer_id == asaas_customer_id).first()
        if not merchant:
            # Lojista não encontrado com esse asaas_customer_id
            return {"status": "ignorado", "motivo": "Lojista não encontrado"}
            
        # PAYMENT_RECEIVED: O cliente pagou a assinatura
        if evento == 'PAYMENT_RECEIVED':
            merchant.status_assinatura = 'ativo'
            # Aqui poderíamos atualizar a data_vencimento baseada no payment.dueDate ou originalDueDate
            db.commit()
            return {"status": "sucesso", "acao": "Assinatura ativada"}
            
        # PAYMENT_OVERDUE: O cliente não pagou e venceu
        elif evento == 'PAYMENT_OVERDUE':
            merchant.status_assinatura = 'inativo'
            db.commit()
            return {"status": "sucesso", "acao": "Assinatura suspensa"}
            
        # PAYMENT_DELETED: A assinatura ou cobrança foi deletada/cancelada
        elif evento == 'PAYMENT_DELETED':
            merchant.status_assinatura = 'cancelado'
            db.commit()
            return {"status": "sucesso", "acao": "Assinatura cancelada"}
            
        return {"status": "ignorado", "motivo": f"Evento {evento} não tratado"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
