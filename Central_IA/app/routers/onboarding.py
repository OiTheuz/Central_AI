from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import re

from app.database import get_public_db
from app.models.merchant import Merchant
from app.models.whatsapp_log import WhatsappMessageLog
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
    
    total_lojas = len(lojas)
    
    # Busca mensagens reais (no banco public, tabela whatsapp_message_log)
    total_mensagens = db.query(WhatsappMessageLog).count()

    total_agendamentos = 0
    merchants_data = []

    for l in lojas:
        # Conta agendamentos reais em cada schema isolado
        agendamentos_loja = 0
        try:
            if l.nome_do_schema:
                res = db.execute(text(f"SELECT count(*) FROM {l.nome_do_schema}.appointments"))
                agendamentos_loja = res.scalar() or 0
                total_agendamentos += agendamentos_loja
        except Exception:
            pass # Ignora caso a tabela ainda não exista

        merchants_data.append({
            "id": l.id,
            "name": l.nome_loja,
            "niche": l.area_atuacao or "Geral",
            "status": "Ativo" if l.meta_access_token else "Pendente (Sem WhatsApp)",
            "date": "Cadastrado"
        })
    
    return {
        "stats": {
            "total_lojas": total_lojas,
            "mensagens_processadas": total_mensagens,
            "agendamentos_hoje": total_agendamentos, # Total de agendamentos no sistema
            "receita_mrr": f"R$ {total_lojas * 150},00" # Custo fixo da assinatura
        },
        "merchants": merchants_data
    }

class SetupWizardRequest(BaseModel):
    lojista_id: int
    horario_abertura: str
    horario_fechamento: str
    horario_almoco_inicio: str = None
    horario_almoco_fim: str = None
    dias_fechados: str = None
    instrucoes_ia: str = None

@router.put("/setup-wizard")
def setup_wizard(body: SetupWizardRequest, db: Session = Depends(get_public_db)):
    """
    Salva as configurações iniciais definidas no Setup Wizard da web.
    """
    merchant = db.query(Merchant).filter(Merchant.id == body.lojista_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")

    merchant.horario_abertura = body.horario_abertura
    merchant.horario_fechamento = body.horario_fechamento
    merchant.horario_almoco_inicio = body.horario_almoco_inicio
    merchant.horario_almoco_fim = body.horario_almoco_fim
    merchant.dias_fechados = body.dias_fechados
    merchant.instrucoes_ia = body.instrucoes_ia

    db.commit()
    return {"status": "sucesso", "mensagem": "Configurações salvas com sucesso!"}

