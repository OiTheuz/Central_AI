from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import re

from app.database import get_public_db
from app.models.merchant import Merchant
from app.services.auth_service import hash_senha
from app.services.schema_service import criar_novo_estabelecimento

router = APIRouter(
    prefix="/api/onboarding",
    tags=["Onboarding"],
)

class SimulatePaymentRequest(BaseModel):
    nome_loja: str
    email: str
    senha: str
    nicho: str
    telefone: str = None

@router.post("/simulate-payment")
def simulate_payment(body: SimulatePaymentRequest, db: Session = Depends(get_public_db)):
    """
    Simula o recebimento de um webhook de pagamento (Stripe/Asaas).
    1. Verifica se email existe.
    2. Cria o schema da loja e copia tabelas.
    3. Registra na tabela public.merchant.
    """
    # 1. Verifica se email já existe
    if db.query(Merchant).filter(Merchant.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    # 2. Gera os identificadores
    slug = re.sub(r'[^a-zA-Z0-9]', '', body.nome_loja.lower())
    codigo_loja = slug
    schema_nome = f"schema_{slug}"

    # Valida colisão de codigo_loja
    if db.query(Merchant).filter(Merchant.codigo_loja == codigo_loja).first():
        codigo_loja = f"{slug}_{db.query(Merchant).count() + 1}"
        schema_nome = f"schema_{codigo_loja}"

    # 3. Cria o schema usando o schema_service
    # Copia as tabelas base
    tabelas_base = ["appointments", "customers", "services"]
    try:
        criar_novo_estabelecimento(schema_nome, tabelas_base, nicho=body.nicho)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar banco de dados: {str(e)}")

    # 4. Registra no public.merchant
    novo_lojista = Merchant(
        nome_loja=body.nome_loja,
        nome_usuario=body.nome_loja,
        email=body.email,
        senha_hash=hash_senha(body.senha),
        codigo_loja=codigo_loja,
        nome_do_schema=schema_nome,
        area_atuacao=body.nicho,
        telefone_contato=body.telefone,
        is_admin=False,
        tem_dashboard=True,
    )
    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    return {
        "status": "sucesso",
        "mensagem": "Pagamento confirmado e Loja criada com sucesso!",
        "lojista_id": novo_lojista.id,
        "schema": schema_nome
    }

@router.get("/admin-merchants")
def get_admin_merchants(db: Session = Depends(get_public_db)):
    """
    Retorna todos os lojistas cadastrados para o Painel Admin do Site.
    (Em produção, proteger com API_KEY ou integrar com JWT do Admin).
    """
    lojas = db.query(Merchant).filter(Merchant.loja_pai_id.is_(None)).order_by(Merchant.id.desc()).all()
    
    # Calcular métricas básicas
    total_lojas = len(lojas)
    
    return {
        "stats": {
            "total_lojas": total_lojas,
            "mensagens_processadas": total_lojas * 150, # Mock de uso
            "agendamentos_hoje": total_lojas * 5, # Mock de uso
            "receita_mrr": f"R$ {total_lojas * 150},00" # Mock assumindo R$ 150/mês
        },
        "merchants": [
            {
                "id": l.id,
                "name": l.nome_loja,
                "niche": l.area_atuacao or "Geral",
                "status": "Ativo" if l.nome_do_schema else "Pendente",
                "date": "Hoje" # Depois pegar data de criacao real
            }
            for l in lojas
        ]
    }

