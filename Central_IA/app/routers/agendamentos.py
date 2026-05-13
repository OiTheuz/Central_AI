from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Merchant
from app.schemas import AgendamentoCreate

router = APIRouter(tags=["Agendamentos"])

# =========================================================
# CRIAR AGENDAMENTO

@router.post("/agendamentos/")
def criar_agendamento(
    agendamento: AgendamentoCreate,
    db: Session = Depends(get_db)
):

    merchant = db.query(Merchant).filter(
        Merchant.codigo_loja == agendamento.codigo_loja
    ).first()

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Lojista não encontrado."
        )

    schema_name = merchant.nome_do_schema

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

        return {
            "mensagem": f"Agendamento para {agendamento.cliente_nome} salvo com sucesso!"
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# LISTAR AGENDAMENTOS

@router.get("/agendamentos/{codigo_loja}")
def listar_agendamentos(
    codigo_loja: str,
    db: Session = Depends(get_db)
):

    merchant = db.query(Merchant).filter(
        Merchant.codigo_loja == codigo_loja
    ).first()

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Lojista não encontrado."
        )

    schema_name = merchant.nome_do_schema

    try:

        comando_sql = text(f"""
            SELECT *
            FROM {schema_name}.agendamentos
            ORDER BY data_horario ASC
        """)

        resultados = db.execute(comando_sql).mappings().all()

        return resultados

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
