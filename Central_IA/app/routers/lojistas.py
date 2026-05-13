from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Merchant
from app.schemas import MerchantCreate, MerchantResponse

router = APIRouter(tags=["Lojistas"])

# =========================================================
# CRIAR LOJISTA

@router.post("/lojistas/", response_model=MerchantResponse)
def criar_lojista(
    merchant: MerchantCreate,
    db: Session = Depends(get_db)
):

    db_merchant = db.query(Merchant).filter(
        (Merchant.codigo_loja == merchant.codigo_loja) |
        (Merchant.nome_do_schema == merchant.nome_do_schema)
    ).first()

    if db_merchant:
        raise HTTPException(
            status_code=400,
            detail="Lojista ou Schema já existe."
        )

    novo_lojista = Merchant(**merchant.model_dump())

    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    try:

        schema_nome = merchant.nome_do_schema

        db.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {schema_nome}")
        )

        db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {schema_nome}.agendamentos (
                id SERIAL PRIMARY KEY,
                cliente_nome VARCHAR(100),
                cliente_whatsapp VARCHAR(20),
                data_horario TIMESTAMP,
                servico VARCHAR(100)
            )
        """))

        db.commit()

        print(f"✅ Schema {schema_nome} criado com sucesso")

    except Exception as e:

        db.rollback()

        print(f"❌ ERRO AO CRIAR SCHEMA: {e}")

    return novo_lojista

# =========================================================
# LISTAR LOJISTAS

@router.get("/lojistas/", response_model=list[MerchantResponse])
def listar_lojistas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    lojistas = db.query(Merchant)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return lojistas
