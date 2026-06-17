import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_public_db, validar_schema
from app.models import Merchant
from app.schemas import MerchantCreate, MerchantResponse
from app.schemas.merchant import MerchantUpdate
from app.services.auth_service import get_lojista_atual, hash_senha
from app.services.schema_service import criar_novo_estabelecimento

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Lojistas"])

# =========================================================
# CRIAR LOJISTA (protegido — apenas admin)

@router.post("/lojistas/", response_model=MerchantResponse)
def criar_lojista(
    merchant: MerchantCreate,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    # Apenas admins podem criar lojistas
    if not admin.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem criar lojistas.",
        )

    db_merchant = db.query(Merchant).filter(
        (Merchant.codigo_loja == merchant.codigo_loja) |
        (Merchant.nome_do_schema == merchant.nome_do_schema) |
        (Merchant.email == merchant.email)
    ).first()

    if db_merchant:
        raise HTTPException(
            status_code=400,
            detail="Lojista, Schema ou E-mail já existe."
        )

    dados = merchant.model_dump(exclude={"senha"})
    dados["senha_hash"] = hash_senha(merchant.senha)

    novo_lojista = Merchant(**dados)

    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    try:
        schema_nome = validar_schema(merchant.nome_do_schema)
        criar_novo_estabelecimento(schema_nome, ["appointments", "customers", "services"])
        logger.info("Schema %s criado com sucesso para lojista %s", schema_nome, merchant.nome_loja)

    except ValueError as e:
        logger.error("Nome do schema inválido: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.warning("Schema pode já existir ou erro não fatal: %s", e)

    return novo_lojista

# =========================================================
# LISTAR LOJISTAS (protegido — apenas admin)

@router.get("/lojistas/", response_model=list[MerchantResponse])
def listar_lojistas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem listar lojistas.",
        )

    lojistas = db.query(Merchant)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return lojistas

# =========================================================
# EDITAR PERMISSÕES DO LOJISTA (protegido — apenas admin)

@router.patch("/lojistas/{lojista_id}", response_model=MerchantResponse)
def editar_lojista(
    lojista_id: int,
    dados: MerchantUpdate,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem editar lojistas.",
        )

    lojista = db.query(Merchant).filter(Merchant.id == lojista_id).first()
    if not lojista:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(lojista, campo, valor)

    db.commit()
    db.refresh(lojista)

    logger.info("Lojista %s atualizado pelo admin %s", lojista_id, admin.id)
    return lojista
