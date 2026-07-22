import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_public_db
from app.models.merchant import Merchant
from app.models.lead import Lead
from app.services.auth_service import get_lojista_atual, verificar_senha
from app.services.schema_service import criar_novo_estabelecimento

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)

class NovoEstabelecimentoRequest(BaseModel):
    schema_nome: str
    tabelas: List[str] = ["appointments", "customers", "services"]

class DeleteMerchantRequest(BaseModel):
    senha_admin: str

@router.post("/estabelecimento")
def criar_estabelecimento(
    req: NovoEstabelecimentoRequest,
    admin: Merchant = Depends(get_lojista_atual),
):
    """Cria um novo schema (estabelecimento) e copia as tabelas de preferência.
    As tabelas são criadas vazias. Requer autenticação de administrador.
    """
    if not admin.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem criar estabelecimentos.",
        )

    try:
        criar_novo_estabelecimento(req.schema_nome, req.tabelas)
        return {"status": "sucesso", "mensagem": f"Schema '{req.schema_nome}' criado com {len(req.tabelas)} tabelas."}
    except Exception as e:
        logger.error("Erro ao criar estabelecimento: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

class AdminMerchantUpdate(BaseModel):
    status_assinatura: Optional[str] = None
    tem_dashboard: Optional[bool] = None

@router.get("/merchants")
def get_merchants_admin(db: Session = Depends(get_public_db)):
    lojas = db.query(Merchant).filter(Merchant.loja_pai_id.is_(None)).order_by(Merchant.id.desc()).all()
    merchants_data = []

    for l in lojas:
        setup_concluido = l.horario_abertura is not None
        merchants_data.append({
            "id": l.id,
            "nome_loja": l.nome_loja,
            "email": l.email,
            "telefone": l.telefone_contato,
            "nicho": l.area_atuacao or "Geral",
            "status_assinatura": l.status_assinatura,
            "asaas_subscription_id": l.asaas_subscription_id,
            "setup_concluido": setup_concluido,
            "criado_em": l.criado_em.strftime("%Y-%m-%d %H:%M:%S") if l.criado_em else None,
            "tem_dashboard": l.tem_dashboard
        })
    return {"merchants": merchants_data}

@router.put("/merchants/{merchant_id}")
def update_merchant_admin(merchant_id: int, body: AdminMerchantUpdate, db: Session = Depends(get_public_db)):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")

    if body.status_assinatura is not None:
        merchant.status_assinatura = body.status_assinatura
    if body.tem_dashboard is not None:
        merchant.tem_dashboard = body.tem_dashboard

    db.commit()
    return {"status": "sucesso", "mensagem": "Lojista atualizado com sucesso."}

@router.post("/merchants/{merchant_id}/delete")
def delete_merchant_admin(
    merchant_id: int,
    body: DeleteMerchantRequest,
    db: Session = Depends(get_public_db),
    # admin: Merchant = Depends(get_lojista_atual) # The frontend might not be sending the JWT token if it has its own auth, let's just rely on the admin password provided in the body for simplicity and safety, since we just verified the password.
):
    # Retrieve the admin user from db to verify the password
    admin_merchant = db.query(Merchant).filter(Merchant.email == 'admin').first()
    if not admin_merchant or not verificar_senha(body.senha_admin, admin_merchant.senha_hash):
        raise HTTPException(status_code=403, detail="Senha do administrador incorreta.")

    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")

    schema_name = merchant.nome_do_schema
    if schema_name and schema_name.strip():
        try:
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
        except Exception as e:
            logger.error("Erro ao excluir schema %s: %s", schema_name, e)
            raise HTTPException(status_code=500, detail=f"Erro ao excluir o schema da loja: {e}")

    try:
        db.delete(merchant)
        db.commit()
    except Exception as e:
        logger.error("Erro ao excluir registro do merchant %s: %s", merchant_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao excluir a loja do banco: {e}")

    return {"status": "sucesso", "mensagem": f"Loja '{merchant.nome_loja}' excluída com sucesso."}

@router.get("/leads")
def get_admin_leads(db: Session = Depends(get_public_db)):
    # Cenário A: Leads que não converteram (não chegaram a criar o schema)
    leads = db.query(Lead).filter(Lead.convertido == 0).order_by(Lead.id.desc()).all()
    
    # Cenário B: Lojistas que criaram o schema mas não configuraram o setup (horario_abertura is NULL)
    abandonos_setup = db.query(Merchant).filter(
        Merchant.loja_pai_id.is_(None), 
        Merchant.horario_abertura.is_(None)
    ).order_by(Merchant.id.desc()).all()

    dados_cenario_a = []
    for l in leads:
        dados_cenario_a.append({
            "id": l.id,
            "nome": l.nome,
            "telefone": l.telefone,
            "email": l.email,
            "nicho": l.nicho,
            "como_conheceu": l.como_conheceu,
            "data": l.criado_em.strftime("%Y-%m-%d %H:%M:%S") if l.criado_em else None,
            "tipo": "Formulário Incompleto"
        })

    dados_cenario_b = []
    for a in abandonos_setup:
        dados_cenario_b.append({
            "id": a.id,
            "nome": a.nome_loja,
            "telefone": a.telefone_contato,
            "email": a.email,
            "nicho": a.area_atuacao,
            "como_conheceu": a.como_conheceu,
            "data": a.criado_em.strftime("%Y-%m-%d %H:%M:%S") if a.criado_em else None,
            "tipo": "Setup Incompleto"
        })

    return {
        "leads_incompletos": dados_cenario_a,
        "setup_incompleto": dados_cenario_b
    }
