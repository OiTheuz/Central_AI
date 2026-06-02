import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_public_db, validar_schema
from app.models import Merchant
from app.schemas import AgendamentoCreate

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Agendamentos"])

# =========================================================
# CRIAR AGENDAMENTO (router legado — mantido por compatibilidade)
# Prefer usar /api/mobile/agendamentos/manual (app_lojista.py)

@router.post("/agendamentos/")
def criar_agendamento(
    agendamento: AgendamentoCreate,
    db: Session = Depends(get_public_db)
):
    merchant = db.query(Merchant).filter(
        Merchant.codigo_loja == agendamento.codigo_loja
    ).first()

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Lojista não encontrado."
        )

    # Validação anti SQL Injection antes de interpolar no SQL
    schema_name = validar_schema(str(merchant.nome_do_schema))

    try:
        comando_sql = text(f"""
            INSERT INTO {schema_name}.agendamentos
            (
                cliente_nome,
                cliente_whatsapp,
                data_horario,
                servico
            )
            VALUES
            (
                :nome,
                :whatsapp,
                :data_hora,
                :serv
            )
        """)

        parametros = {
            "nome": agendamento.cliente_nome,
            "whatsapp": agendamento.cliente_whatsapp,
            "data_hora": agendamento.data_horario,
            "serv": agendamento.servico
        }

        db.execute(comando_sql, parametros)
        db.commit()

        logger.info("Agendamento legado criado: loja=%s cliente=%s", schema_name, agendamento.cliente_nome)
        return {"mensagem": f"Agendamento para {agendamento.cliente_nome} salvo com sucesso!"}

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error("Erro ao criar agendamento legado: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# LISTAR AGENDAMENTOS (router legado)

@router.get("/agendamentos/{codigo_loja}")
def listar_agendamentos(
    codigo_loja: str,
    db: Session = Depends(get_public_db)
):
    merchant = db.query(Merchant).filter(
        Merchant.codigo_loja == codigo_loja
    ).first()

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Lojista não encontrado."
        )

    # Validação anti SQL Injection
    schema_name = validar_schema(str(merchant.nome_do_schema))

    try:
        comando_sql = text(f"""
            SELECT *
            FROM {schema_name}.agendamentos
            ORDER BY data_horario ASC
            LIMIT 200
        """)

        resultados = db.execute(comando_sql).mappings().all()
        return resultados

    except Exception as e:
        logger.error("Erro ao listar agendamentos legado: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
