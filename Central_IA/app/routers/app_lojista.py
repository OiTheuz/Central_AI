# ============================================================
# Router do App Lojista — Endpoints protegidos por JWT
# Todas as rotas usam o schema do lojista autenticado
# ============================================================

import logging
import re
import uuid
import asyncio
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.dependencies import get_db
from app.database import validar_schema
from app.models import Merchant
from app.services.auth_service import get_lojista_atual
from app.services.whatsapp_service import enviar_mensagem_whatsapp
from app.services.push_service import enviar_notificacao_push
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/mobile",
    tags=["App Lojista"],
)


# ─── Helper: Serialização de agendamento ────────────────────

def _serializar_agendamento(row) -> dict:
    """Serializa uma row de agendamento para o formato JSON do app."""
    reag_data = row["reagendamento_data"] if "reagendamento_data" in row.keys() else None
    reag_hora = row["reagendamento_hora"] if "reagendamento_hora" in row.keys() else None
    return {
        "id": row["id"],
        "clienteNome": row["cliente_nome"] or "Cliente",
        "clienteTelefone": row["cliente_telefone"] or "",
        "servico": row["servico"] or "Serviço não especificado",
        "data": str(row["data_agendamento"]),
        "hora": row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "--:--",
        "status": row["status"],
        "origem": (row["origem"] or "manual").lower(),
        "numeroTicket": row["numero_ticket"] if "numero_ticket" in row.keys() else None,
        "tipoPendencia": row["tipo_pendencia"] if "tipo_pendencia" in row.keys() else None,
        "reagendamentoData": str(reag_data) if reag_data else None,
        "reagendamentoHora": reag_hora.strftime("%H:%M") if reag_hora else None,
        "motivoCancelamento": row["motivo_cancelamento"] if "motivo_cancelamento" in row.keys() else None,
    }

async def _broadcast_refresh(schema_name: str):
    try:
        await manager.broadcast_to_schema(schema_name, {"type": "REFRESH_APPOINTMENTS"})
    except Exception as e:
        logger.error("Erro no broadcast: %s", e)



# =========================================================
# REGISTRAR PUSH TOKEN DO LOJISTA
# =========================================================

class PushTokenRequest(BaseModel):
    token: str

@router.post("/push-token")
def registrar_push_token(
    body: PushTokenRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Salva o Expo Push Token do lojista no banco para notificações."""
    try:
        # Atualiza a tabela merchant global (não no schema do lojista)
        db.execute(
            text("UPDATE merchant SET push_token = :token WHERE id = :m_id"),
            {"token": body.token, "m_id": merchant.id}
        )
        db.commit()
        logger.info("Push token atualizado para merchant_id=%s", merchant.id)
        return {"status": "sucesso", "mensagem": "Push token salvo."}
    except Exception as e:
        db.rollback()
        logger.error("Erro ao salvar push token: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# AGENDAMENTOS DE HOJE (status aprovado/confirmado)
# =========================================================

@router.get("/agendamentos/hoje")
def obter_agendamentos_hoje(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna agendamentos de hoje com status aprovado ou confirmado."""


    query = text("""
        SELECT 
            a.id, 
            c.nome AS cliente_nome,
            c.telefone_whatsapp AS cliente_telefone,
            s.nome AS servico, 
            a.data_agendamento, 
            a.horario_agendamento,
            a.status,
            a.origem,
            a.numero_ticket,
            a.tipo_pendencia,
            a.reagendamento_data,
            a.reagendamento_hora,
            a.motivo_cancelamento
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.data_agendamento = :hoje
          AND a.status IN ('aprovado', 'confirmado')
        ORDER BY a.horario_agendamento ASC
        LIMIT 200
    """)

    resultados = db.execute(query, {"hoje": date.today()}).mappings().all()
    agendamentos = [_serializar_agendamento(row) for row in resultados]

    return {"status": "sucesso", "total": len(agendamentos), "dados": agendamentos}


# =========================================================
# AGENDAMENTOS PENDENTES (para a aba "Pendentes")
# =========================================================

@router.get("/agendamentos/pendentes")
def obter_agendamentos_pendentes(
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna todos os agendamentos com status pendente (paginado)."""


    offset = (page - 1) * size

    query = text("""
        SELECT 
            a.id,
            c.nome AS cliente_nome,
            c.telefone_whatsapp AS cliente_telefone,
            s.nome AS servico,
            a.data_agendamento,
            a.horario_agendamento,
            a.status,
            a.origem,
            a.numero_ticket,
            a.tipo_pendencia,
            a.reagendamento_data,
            a.reagendamento_hora,
            a.motivo_cancelamento
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status = 'pendente'
        ORDER BY a.data_agendamento ASC, a.horario_agendamento ASC
        LIMIT :size OFFSET :offset
    """)

    resultados = db.execute(query, {"size": size, "offset": offset}).mappings().all()
    agendamentos = [_serializar_agendamento(row) for row in resultados]

    return {"status": "sucesso", "total": len(agendamentos), "dados": agendamentos}


# =========================================================
# AGENDAMENTOS POR DATA (para o calendário)
# =========================================================

@router.get("/agendamentos/data/{data}")
def obter_agendamentos_por_data(
    data: str,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna agendamentos de uma data específica (YYYY-MM-DD). Apenas aprovados/confirmados/concluidos."""

    # Validação do formato de data
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

    query = text("""
        SELECT 
            a.id,
            c.nome AS cliente_nome,
            c.telefone_whatsapp AS cliente_telefone,
            s.nome AS servico,
            a.data_agendamento,
            a.horario_agendamento,
            a.status,
            a.origem,
            a.numero_ticket,
            a.tipo_pendencia,
            a.reagendamento_data,
            a.reagendamento_hora,
            a.motivo_cancelamento
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.data_agendamento = :data
          AND a.status IN ('aprovado', 'confirmado', 'concluido')
        ORDER BY a.horario_agendamento ASC
        LIMIT 200
    """)

    resultados = db.execute(query, {"data": data}).mappings().all()
    agendamentos = [_serializar_agendamento(row) for row in resultados]

    return {"status": "sucesso", "total": len(agendamentos), "dados": agendamentos}


# =========================================================
# =========================================================
# CONFIRMAR REAGENDAMENTO (lojista aceita e pode alterar data/hora)
# =========================================================

class ConfirmarReagendamentoRequest(BaseModel):
    nova_data: str
    nova_hora: str

@router.put("/agendamentos/{agendamento_id}/confirmar-reagendamento")
def confirmar_reagendamento(
    agendamento_id: int,
    body: ConfirmarReagendamentoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Confirma um reagendamento: remove a pendência e notifica o cliente."""
    row = db.execute(text("""
        SELECT a.*, c.telefone_whatsapp, c.nome AS cliente_nome, s.nome AS servico_nome
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.id = :id AND a.tipo_pendencia = 'reagendamento' AND a.status = 'pendente'
    """), {"id": agendamento_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Pendência de reagendamento não encontrada.")

    try:
        from datetime import datetime as dt
        nova_data_obj = dt.strptime(body.nova_data, "%Y-%m-%d").date()
        nova_hora_obj = dt.strptime(body.nova_hora, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data/hora inválido. Use YYYY-MM-DD e HH:MM.")

    try:
        # 1. Remove a pendência de reagendamento
        db.execute(text("DELETE FROM appointments WHERE id = :id"), {"id": agendamento_id})
        
        # 2. Atualiza o agendamento original
        db.execute(text("""
            UPDATE appointments
            SET data_agendamento = :nova_data, horario_agendamento = :nova_hora
            WHERE numero_ticket = :ticket AND status IN ('aprovado', 'confirmado')
        """), {
            "nova_data": nova_data_obj,
            "nova_hora": nova_hora_obj,
            "ticket": row["numero_ticket"]
        })
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))

    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            nome = row["cliente_nome"] or ""
            servico = row["servico_nome"] or "serviço"
            data_fmt = nova_data_obj.strftime("%d/%m/%Y")
            hora_fmt = nova_hora_obj.strftime("%H:%M")
            msg = (
                f"Boa notícia{', ' + nome if nome and nome != 'Cliente' else ''}! ✅ "
                f"Seu reagendamento para {servico} foi confirmado para o dia "
                f"*{data_fmt} às {hora_fmt}*. Estamos te esperando! Até logo! 👋"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=msg, phone_number_id=merchant.numero_whatsapp)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de confirmação de reagendamento: %s", e)

    try:
        if merchant.push_token:
            enviar_notificacao_push(
                push_token=str(merchant.push_token),
                titulo="Reagendamento Confirmado ✅",
                corpo=f"Reagendamento de {row.get('cliente_nome') or 'Cliente'} confirmado para {nova_data_obj.strftime('%d/%m/%Y')} às {nova_hora_obj.strftime('%H:%M')}.",
                dados={"tela": "home"}
            )
    except Exception as e:
        logger.warning("Erro ao enviar push de reagendamento: %s", e)

    return {"status": "sucesso", "mensagem": "Reagendamento confirmado e cliente notificado!"}


# =========================================================
# RECUSAR REAGENDAMENTO
# =========================================================

@router.put("/agendamentos/{agendamento_id}/recusar-reagendamento")
def recusar_reagendamento(
    agendamento_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Recusa um reagendamento: remove a pendência e avisa o cliente via WhatsApp."""
    row = db.execute(text("""
        SELECT a.*, c.telefone_whatsapp, c.nome AS cliente_nome, s.nome AS servico_nome
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.id = :id AND a.tipo_pendencia = 'reagendamento' AND a.status = 'pendente'
    """), {"id": agendamento_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Pendência de reagendamento não encontrada.")

    try:
        db.execute(text("DELETE FROM appointments WHERE id = :id"), {"id": agendamento_id})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))

    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            nome = row["cliente_nome"] or ""
            servico = row["servico_nome"] or "serviço"
            reag_data = row.get("reagendamento_data")
            reag_hora = row.get("reagendamento_hora")
            data_fmt = reag_data.strftime("%d/%m/%Y") if reag_data else "??/??/????"
            hora_fmt = reag_hora.strftime("%H:%M") if reag_hora else "??:??"
            msg = (
                f"Olá{', ' + nome if nome and nome != 'Cliente' else ''}! 😊 "
                f"Infelizmente não foi possível realizar o reagendamento do seu {servico} para "
                f"{data_fmt} às {hora_fmt}. "
                f"Por favor, entre em contato conosco para encontrarmos a melhor solução. "
                f"Qualquer dúvida, é só mandar um *Oi*! 👋"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=msg, phone_number_id=merchant.numero_whatsapp)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de recusa de reagendamento: %s", e)

    try:
        if merchant.push_token:
            enviar_notificacao_push(
                push_token=str(merchant.push_token),
                titulo="Reagendamento Recusado ❌",
                corpo=f"Reagendamento de {row.get('cliente_nome') or 'Cliente'} recusado.",
                dados={"tela": "home"}
            )
    except Exception as e:
        logger.warning("Erro ao enviar push de recusa: %s", e)

    return {"status": "sucesso", "mensagem": "Reagendamento recusado e cliente notificado."}


# =========================================================
# ACEITAR CANCELAMENTO
# =========================================================

@router.put("/agendamentos/{agendamento_id}/aceitar-cancelamento")
def aceitar_cancelamento(
    agendamento_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Aceita um cancelamento: muda status para 'cancelado' e avisa o cliente via WhatsApp."""
    row = db.execute(text("""
        SELECT a.*, c.telefone_whatsapp, c.nome AS cliente_nome, s.nome AS servico_nome
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.id = :id AND a.tipo_pendencia = 'cancelamento' AND a.status = 'pendente'
    """), {"id": agendamento_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Pendência de cancelamento não encontrada.")

    try:
        # 1. Remove a pendência de cancelamento
        db.execute(text("DELETE FROM appointments WHERE id = :id"), {"id": agendamento_id})
        
        # 2. Atualiza o agendamento original para cancelado
        db.execute(text("""
            UPDATE appointments
            SET status = 'cancelado', motivo_cancelamento = :motivo
            WHERE numero_ticket = :ticket AND status IN ('aprovado', 'confirmado', 'pendente')
        """), {
            "motivo": row["motivo_cancelamento"],
            "ticket": row["numero_ticket"]
        })
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))

    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            nome = row["cliente_nome"] or ""
            servico = row["servico_nome"] or "serviço"
            data_orig = row.get("data_agendamento")
            hora_orig = row.get("horario_agendamento")
            data_fmt = data_orig.strftime("%d/%m/%Y") if data_orig else "??/??/????"
            hora_fmt = hora_orig.strftime("%H:%M") if hora_orig else "??:??"
            main_merchant = db.query(Merchant).filter(Merchant.nome_do_schema == merchant.nome_do_schema, Merchant.loja_pai_id == None).first()
            nome_loja = main_merchant.nome_loja if main_merchant and main_merchant.nome_loja else (merchant.nome_loja or "o estabelecimento")
            
            msg = (
                f"Olá{', ' + nome if nome and nome != 'Cliente' else ''}! 😊 "
                f"A *{nome_loja}* recebeu sua solicitação de cancelamento do *{servico}* "
                f"marcado para {data_fmt} às {hora_fmt} e está ciente.\n\n"
                f"Sentiremos a sua falta! Quando quiser voltar, é só mandar um *Oi* "
                f"e agendamos novamente. Até logo! 👋"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=msg, phone_number_id=merchant.numero_whatsapp)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de cancelamento: %s", e)

    try:
        if merchant.push_token:
            enviar_notificacao_push(
                push_token=str(merchant.push_token),
                titulo="Cancelamento Aceito ✅",
                corpo=f"Cancelamento de {row.get('cliente_nome') or 'Cliente'} processado com sucesso.",
                dados={"tela": "home"}
            )
    except Exception as e:
        logger.warning("Erro ao enviar push de cancelamento: %s", e)

    return {"status": "sucesso", "mensagem": "Cancelamento aceito e cliente notificado!"}


# =========================================================
# DATAS COM COMPROMISSOS (dots no calendário)
# =========================================================

@router.get("/agendamentos/datas-com-compromissos")
def obter_datas_com_compromissos(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna array de datas únicas que possuem agendamentos (aprovados/confirmados/concluidos)."""


    query = text("""
        SELECT DISTINCT data_agendamento 
        FROM appointments 
        WHERE status IN ('aprovado', 'confirmado', 'concluido')
        ORDER BY data_agendamento
        LIMIT 366
    """)

    resultados = db.execute(query).fetchall()
    datas = [str(row[0]) for row in resultados]

    return {"status": "sucesso", "datas": datas}


# =========================================================
# APROVAR AGENDAMENTO (pendente → aprovado) + WhatsApp
# =========================================================

from fastapi import BackgroundTasks

@router.put("/agendamentos/{agendamento_id}/aprovar")
def aprovar_agendamento(
    agendamento_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Muda status do agendamento para 'aprovado' e envia mensagem
    de confirmação ao cliente via WhatsApp.
    """


    # Buscar agendamento com dados do cliente e serviço
    query = text("""
        SELECT 
            a.id, a.status, a.data_agendamento, a.horario_agendamento,
            c.nome AS cliente_nome, c.telefone_whatsapp,
            s.nome AS servico_nome
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.id = :id
    """)

    row = db.execute(query, {"id": agendamento_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    if row["status"] != "pendente":
        raise HTTPException(status_code=400, detail=f"Agendamento já está com status '{row['status']}'.")

    # Atualizar status
    try:
        db.execute(
            text("UPDATE appointments SET status = 'aprovado' WHERE id = :id"),
            {"id": agendamento_id},
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Erro ao aprovar agendamento %s: %s", agendamento_id, e)
        raise HTTPException(status_code=500, detail="Falha ao atualizar o status do agendamento.")

    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))
    logger.info("Agendamento %s aprovado pelo lojista %s", agendamento_id, merchant.id)

    # Enviar confirmação via WhatsApp ao cliente
    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            nome_cliente = row["cliente_nome"] if row["cliente_nome"] and row["cliente_nome"] != "Cliente" else ""
            servico = row["servico_nome"] or "serviço"
            data_fmt = row["data_agendamento"].strftime("%d/%m/%Y") if row["data_agendamento"] else "??/??/????"
            hora_fmt = row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "??:??"
            
            if nome_cliente:
                mensagem = f"Tudo certo, {nome_cliente}! ✅ O seu agendamento para {servico} foi confirmadíssimo para o dia {data_fmt} às {hora_fmt}. Estamos te esperando! Até logo! 👋"
            else:
                mensagem = f"Tudo certo! ✅ O seu agendamento para {servico} foi confirmadíssimo para o dia {data_fmt} às {hora_fmt}. Estamos te esperando! Até logo! 👋"
                
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem, phone_number_id=merchant.numero_whatsapp)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de aprovação: %s", e)

    return {"status": "sucesso", "mensagem": "Agendamento aprovado e cliente notificado!"}


# =========================================================
# RECUSAR AGENDAMENTO (pendente → recusado) + WhatsApp
# =========================================================

@router.put("/agendamentos/{agendamento_id}/recusar")
def recusar_agendamento(
    agendamento_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Muda status do agendamento para 'recusado' e envia mensagem
    de aviso ao cliente via WhatsApp.
    """


    query = text("""
        SELECT 
            a.id, a.status, a.data_agendamento, a.horario_agendamento,
            c.nome AS cliente_nome, c.telefone_whatsapp,
            s.nome AS servico_nome
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.id = :id
    """)

    row = db.execute(query, {"id": agendamento_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    if row["status"] != "pendente":
        raise HTTPException(status_code=400, detail=f"Agendamento já está com status '{row['status']}'.")

    # Atualizar status — com rollback explícito em caso de falha
    try:
        db.execute(
            text("UPDATE appointments SET status = 'recusado' WHERE id = :id"),
            {"id": agendamento_id},
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Erro ao recusar agendamento %s: %s", agendamento_id, e)
        raise HTTPException(status_code=500, detail="Falha ao atualizar o status do agendamento.")

    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))
    logger.info("Agendamento %s recusado pelo lojista %s", agendamento_id, merchant.id)

    # Enviar aviso via WhatsApp ao cliente
    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            # Monta contexto do agendamento para o cliente saber qual foi recusado
            data_fmt = row["data_agendamento"].strftime("%d/%m/%Y") if row["data_agendamento"] else None
            hora_fmt = row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else None
            servico = row["servico_nome"]

            # Linha de contexto opcional (ex: "para Corte de Cabelo em 12/06 às 14:00")
            if servico and data_fmt and hora_fmt:
                contexto = f" para *{servico}* em {data_fmt} às {hora_fmt}"
            elif servico:
                contexto = f" para *{servico}*"
            else:
                contexto = ""

            main_merchant = db.query(Merchant).filter(Merchant.nome_do_schema == merchant.nome_do_schema, Merchant.loja_pai_id == None).first()
            nome_loja = main_merchant.nome_loja if main_merchant and main_merchant.nome_loja else (merchant.nome_loja or "o estabelecimento")
            
            mensagem = (
                f"Infelizmente, a *{nome_loja}* precisou recusar a sua solicitação{contexto}. "
                f"Mas você pode fazer um novo agendamento! "
                f"É só mandar um *Oi* para recomeçarmos. 😊"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem, phone_number_id=merchant.numero_whatsapp)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de recusa: %s", e)

    return {"status": "sucesso", "mensagem": "Agendamento recusado e cliente notificado."}


# =========================================================
# CANCELAR AGENDAMENTO (qualquer status → cancelado) + WhatsApp
# =========================================================

@router.put("/agendamentos/{agendamento_id}/cancelar")
def cancelar_agendamento(
    agendamento_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Cancela um agendamento (qualquer status que não seja já cancelado/recusado)
    e envia mensagem de aviso ao cliente via WhatsApp.
    """

    query = text("""
        SELECT
            a.id, a.status, a.data_agendamento, a.horario_agendamento,
            c.nome AS cliente_nome, c.telefone_whatsapp,
            s.nome AS servico_nome
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.id = :id
    """)

    row = db.execute(query, {"id": agendamento_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    if row["status"] in ("cancelado", "recusado"):
        raise HTTPException(
            status_code=400,
            detail=f"Agendamento já está com status '{row['status']}' e não pode ser cancelado novamente."
        )

    try:
        db.execute(
            text("UPDATE appointments SET status = 'cancelado' WHERE id = :id"),
            {"id": agendamento_id},
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Erro ao cancelar agendamento %s: %s", agendamento_id, e)
        raise HTTPException(status_code=500, detail="Falha ao atualizar o status do agendamento.")

    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))
    logger.info("Agendamento %s cancelado pelo lojista %s", agendamento_id, merchant.id)

    # Enviar aviso via WhatsApp ao cliente
    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            data_fmt = row["data_agendamento"].strftime("%d/%m/%Y") if row["data_agendamento"] else "data não informada"
            servico = row["servico_nome"] or "serviço"
            main_merchant = db.query(Merchant).filter(Merchant.nome_do_schema == merchant.nome_do_schema, Merchant.loja_pai_id == None).first()
            nome_loja = main_merchant.nome_loja if main_merchant and main_merchant.nome_loja else (merchant.nome_loja or "o estabelecimento")

            mensagem = (
                f"Olá! Informamos que a *{nome_loja}* realizou o cancelamento "
                f"do seu agendamento do serviço *{servico}* no dia *{data_fmt}*.\n\n"
                f"Se desejar reagendar, é só mandar um *Oi*! 😊"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem, phone_number_id=merchant.numero_whatsapp)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de cancelamento: %s", e)

    return {"status": "sucesso", "mensagem": "Agendamento cancelado e cliente notificado."}


# =========================================================
# REMANEJAR AGENDAMENTO (nova data/hora) + WhatsApp
# =========================================================

class RemanejamentoRequest(BaseModel):
    nova_data: str   # YYYY-MM-DD
    nova_hora: str   # HH:MM


@router.put("/agendamentos/{agendamento_id}/remanejar")
def remanejar_agendamento(
    agendamento_id: int,
    body: RemanejamentoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Atualiza a data e horário de um agendamento e notifica o cliente
    com o horário antigo e o novo via WhatsApp.
    """

    # Validação de formato
    try:
        datetime.strptime(body.nova_data, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de nova_data inválido. Use YYYY-MM-DD.")
    try:
        datetime.strptime(body.nova_hora, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de nova_hora inválido. Use HH:MM.")

    query = text("""
        SELECT
            a.id, a.status, a.data_agendamento, a.horario_agendamento,
            c.nome AS cliente_nome, c.telefone_whatsapp,
            s.nome AS servico_nome
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.id = :id
    """)

    row = db.execute(query, {"id": agendamento_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    if row["status"] in ("cancelado", "recusado"):
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível remanejar um agendamento com status '{row['status']}'."
        )

    # Guardar data/hora antigas antes de atualizar
    data_antiga_fmt = row["data_agendamento"].strftime("%d/%m/%Y") if row["data_agendamento"] else "?"
    hora_antiga_fmt = row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "?"

    try:
        db.execute(
            text("""
                UPDATE appointments
                SET data_agendamento = :nova_data,
                    horario_agendamento = :nova_hora
                WHERE id = :id
            """),
            {"nova_data": body.nova_data, "nova_hora": body.nova_hora, "id": agendamento_id},
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Erro ao remanejar agendamento %s: %s", agendamento_id, e)
        raise HTTPException(status_code=500, detail="Falha ao atualizar o agendamento.")

    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))
    logger.info(
        "Agendamento %s remanejado pelo lojista %s: %s %s → %s %s",
        agendamento_id, merchant.id,
        data_antiga_fmt, hora_antiga_fmt,
        body.nova_data, body.nova_hora,
    )

    # Formatar nova data/hora para exibição
    try:
        nova_data_fmt = datetime.strptime(body.nova_data, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        nova_data_fmt = body.nova_data

    # Enviar aviso via WhatsApp ao cliente
    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            servico = row["servico_nome"] or "serviço"
            main_merchant = db.query(Merchant).filter(Merchant.nome_do_schema == merchant.nome_do_schema, Merchant.loja_pai_id == None).first()
            nome_loja = main_merchant.nome_loja if main_merchant and main_merchant.nome_loja else (merchant.nome_loja or "o estabelecimento")

            mensagem = (
                f"Olá! A *{nome_loja}* realizou uma alteração no seu agendamento "
                f"do serviço *{servico}*, passando do dia/horário "
                f"*{data_antiga_fmt} às {hora_antiga_fmt}* "
                f"para *{nova_data_fmt} às {body.nova_hora}*.\n\n"
                f"Se tiver alguma dúvida, é só falar! 😊"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem, phone_number_id=merchant.numero_whatsapp)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de remanejamento: %s", e)

    return {
        "status": "sucesso",
        "mensagem": f"Agendamento remanejado para {nova_data_fmt} às {body.nova_hora}. Cliente notificado."
    }


# =========================================================
# SERVIÇOS DO LOJISTA
# =========================================================


@router.get("/servicos")
def obter_servicos(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Lista todos os serviços cadastrados no schema do lojista."""


    # CORREÇÃO: A coluna real no banco é duracao_minutos
    resultados = db.execute(text("SELECT id, nome, preco, duracao_minutos AS duracao FROM services ORDER BY nome")).mappings().all()

    servicos = []
    for row in resultados:
        servicos.append({
            "id": row["id"],
            "nome": row["nome"],
            "preco": float(row["preco"]) if row.get("preco") else 0,
            "duracao": int(row["duracao"]) if row.get("duracao") else 0,
        })

    return {"status": "sucesso", "dados": servicos}


class ServicoRequest(BaseModel):
    nome: str
    preco: float
    duracao: int


@router.post("/servicos")
def criar_servico(
    body: ServicoRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Cria um novo serviço no schema do lojista."""

    if not merchant.pode_editar_servicos:
        raise HTTPException(status_code=403, detail="Você não tem permissão para adicionar serviços.")


    if not body.nome.strip():
        raise HTTPException(status_code=400, detail="O nome do serviço é obrigatório.")

    try:
        db.execute(text("""
            INSERT INTO services (nome, preco, duracao_minutos)
            VALUES (:nome, :preco, :duracao)
        """), {
            "nome": body.nome.strip(),
            "preco": body.preco,
            "duracao": body.duracao,
        })
        db.commit()
        logger.info("Serviço criado: %s pelo lojista %s", body.nome, merchant.id)
        return {"status": "sucesso", "mensagem": "Serviço criado."}
    except Exception as e:
        db.rollback()
        logger.error("Erro ao criar serviço: %s", e)
        raise HTTPException(status_code=500, detail="Falha ao criar serviço.")


@router.put("/servicos/{servico_id}")
def atualizar_servico(
    servico_id: int,
    body: ServicoRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Atualiza um serviço existente."""

    if not merchant.pode_editar_servicos:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar serviços.")


    if not body.nome.strip():
        raise HTTPException(status_code=400, detail="O nome do serviço é obrigatório.")

    # Verifica se existe
    serv = db.execute(text("SELECT id FROM services WHERE id = :id"), {"id": servico_id}).fetchone()
    if not serv:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")

    try:
        db.execute(text("""
            UPDATE services 
            SET nome = :nome, preco = :preco, duracao_minutos = :duracao
            WHERE id = :id
        """), {
            "id": servico_id,
            "nome": body.nome.strip(),
            "preco": body.preco,
            "duracao": body.duracao,
        })
        db.commit()
        return {"status": "sucesso", "mensagem": "Serviço atualizado."}
    except Exception as e:
        db.rollback()
        logger.error("Erro ao atualizar serviço %s: %s", servico_id, e)
        raise HTTPException(status_code=500, detail="Falha ao atualizar serviço.")


@router.delete("/servicos/{servico_id}")
def excluir_servico(
    servico_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Exclui um serviço existente."""

    if not merchant.pode_editar_servicos:
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir serviços.")


    # Verifica se existe
    serv = db.execute(text("SELECT id FROM services WHERE id = :id"), {"id": servico_id}).fetchone()
    if not serv:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")

    try:
        db.execute(text("DELETE FROM services WHERE id = :id"), {"id": servico_id})
        db.commit()
        return {"status": "sucesso", "mensagem": "Serviço excluído."}
    except Exception as e:
        db.rollback()
        logger.error("Erro ao excluir serviço %s: %s", servico_id, e)
        raise HTTPException(status_code=500, detail="Possivelmente o serviço está vinculado a agendamentos.")
# =========================================================
# AGENDAMENTO MANUAL (criado pelo lojista no app)
# =========================================================

# ── Limite máximo de ocorrências (segurança no servidor) ──
_MAX_OCORRENCIAS = 52


class AgendamentoManualRequest(BaseModel):
    clienteNome: str
    clienteTelefone: str
    servicoId: int
    data: str           # YYYY-MM-DD
    hora: str           # HH:MM
    # Campos de recorrência — opcionais para retrocompatibilidade
    isRecorrente: bool = False
    frequencia: str | None = None   # 'semanal' | 'mensal'
    ocorrencias: int | None = None  # 1–52
    isPacotePrePago: bool = False
    valorTotalPacote: float | None = None


@router.post("/agendamentos/manual")
def criar_agendamento_manual(
    body: AgendamentoManualRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Cria um agendamento manualmente pelo lojista.
    Suporta agendamento único ou recorrente (semanal/mensal) com bulk insert.
    """

    try:
        # ── 1. Validar serviço ──
        servico = db.execute(
            text("SELECT id, nome FROM services WHERE id = :sid"),
            {"sid": body.servicoId}
        ).mappings().fetchone()

        if not servico:
            raise HTTPException(status_code=404, detail="Serviço não encontrado.")

        # ── 2. Validar campos de recorrência ──
        if body.isRecorrente:
            if body.frequencia not in ("semanal", "mensal"):
                raise HTTPException(
                    status_code=400,
                    detail="Campo 'frequencia' deve ser 'semanal' ou 'mensal'."
                )
            if not body.ocorrencias or body.ocorrencias < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Campo 'ocorrencias' deve ser um inteiro >= 1."
                )
            # Impõe o limite de segurança do servidor
            n_ocorrencias = min(body.ocorrencias, _MAX_OCORRENCIAS)
        else:
            n_ocorrencias = 1

        # ── 3. Upsert do cliente pelo telefone ──
        cliente_id = db.execute(
            text("""
                INSERT INTO customers (nome, telefone_whatsapp)
                VALUES (:nome, :tel)
                ON CONFLICT (telefone_whatsapp) DO UPDATE SET nome = EXCLUDED.nome
                RETURNING id
            """),
            {"nome": body.clienteNome, "tel": body.clienteTelefone}
        ).scalar()

        if not cliente_id:
            raise HTTPException(status_code=500, detail="Falha ao localizar cliente após insert.")

        # ── 4. Gerar lista de datas ──
        try:
            data_base = datetime.strptime(body.data, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

        datas: list[date] = []
        for i in range(n_ocorrencias):
            if body.isRecorrente and body.frequencia == "mensal":
                datas.append(data_base + relativedelta(months=i))
            else:
                # Semanal ou agendamento único (i=0 → mesma data)
                datas.append(data_base + timedelta(weeks=i))

        # ── 5. Bulk insert ──
        recurrence_id = str(uuid.uuid4()) if body.isRecorrente and n_ocorrencias > 1 else None

        max_ticket = db.execute(
            text("SELECT COALESCE(MAX(numero_ticket), 0) FROM appointments")
        ).scalar() or 0

        registros = []
        for i, d in enumerate(datas):
            valor_cobrado = None
            is_paid_in_package = False

            if body.isRecorrente and body.isPacotePrePago:
                if i == 0:
                    valor_cobrado = body.valorTotalPacote
                else:
                    valor_cobrado = 0.0
                    is_paid_in_package = True

            registros.append({
                "c_id": cliente_id,
                "s_id": body.servicoId,
                "data": str(d),
                "hora": body.hora,
                "rec_id": recurrence_id,
                "valor": valor_cobrado,
                "is_paid": is_paid_in_package,
                "numero_ticket": max_ticket + i + 1,
            })

        db.execute(
            text("""
                INSERT INTO appointments
                    (customer_id, service_id, data_agendamento, horario_agendamento,
                     status, origem, recurrence_id, valor_cobrado, is_paid_in_package, numero_ticket)
                VALUES
                    (:c_id, :s_id, :data, :hora, 'aprovado', 'manual', :rec_id, :valor, :is_paid, :numero_ticket)
            """),
            registros,
        )
        db.commit()
        background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))

        total = len(datas)
        logger.info(
            "Agendamento(s) manual(is) criado(s) pelo lojista %s: %s — %d ocorrencia(s) a partir de %s | recurrence_id=%s",
            merchant.id, servico["nome"], total, body.data, recurrence_id or "N/A"
        )

        if body.isRecorrente and total > 1:
            freq_label = "semanas" if body.frequencia == "semanal" else "meses"
            mensagem = (
                f"{total} agendamentos de {body.clienteNome} para {servico['nome']} "
                f"criados com sucesso! ({total} {freq_label} a partir de {datas[0].strftime('%d/%m/%Y')})"
            )
        else:
            mensagem = f"Agendamento de {body.clienteNome} para {servico['nome']} criado com sucesso!"

        return {
            "status": "sucesso",
            "mensagem": mensagem,
            "total_criados": total,
            "recurrence_id": recurrence_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao criar agendamento manual para lojista %s: %s", merchant.id, e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# MÉTRICAS DE HOJE
# =========================================================

@router.get("/metricas/hoje")
def obter_metricas_hoje(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna contagem de atendimentos e ganhos previstos para hoje."""


    # Total de agendamentos de hoje (aprovados)
    contagem = db.execute(text("""
        SELECT COUNT(*) FROM appointments 
        WHERE data_agendamento = :hoje 
          AND status IN ('aprovado', 'confirmado')
    """), {"hoje": date.today()}).scalar() or 0

    # Ganhos previstos (soma dos preços dos serviços)
    ganhos = db.execute(text("""
        SELECT COALESCE(SUM(s.preco), 0) 
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.data_agendamento = :hoje
          AND a.status IN ('aprovado', 'confirmado')
    """), {"hoje": date.today()}).scalar() or 0

    # Próximo aniversariante
    # Suporta data no formato YYYY-MM-DD ou DD/MM/YYYY
    aniversariante_row = db.execute(text("""
        WITH aniversarios AS (
            SELECT id, nome, data_nascimento,
                   CASE 
                     WHEN SUBSTRING(data_nascimento, 3, 1) = '/' THEN SUBSTRING(data_nascimento, 4, 2) || '-' || SUBSTRING(data_nascimento, 1, 2)
                     WHEN SUBSTRING(data_nascimento, 5, 1) = '-' THEN SUBSTRING(data_nascimento, 6, 5)
                     ELSE NULL
                   END as mm_dd
            FROM customers
            WHERE data_nascimento IS NOT NULL AND LENGTH(data_nascimento) = 10
        )
        SELECT id, nome, data_nascimento, 
               (mm_dd = TO_CHAR(CURRENT_DATE, 'MM-DD')) as is_hoje
        FROM aniversarios
        WHERE mm_dd IS NOT NULL
        ORDER BY
          mm_dd < TO_CHAR(CURRENT_DATE, 'MM-DD'),
          mm_dd
        LIMIT 1
    """)).mappings().first()

    proximo_aniversariante = None
    if aniversariante_row:
        proximo_aniversariante = {
            "id": aniversariante_row["id"],
            "nome": aniversariante_row["nome"],
            "data_nascimento": aniversariante_row["data_nascimento"],
            "is_hoje": bool(aniversariante_row["is_hoje"])
        }

    return {
        "status": "sucesso",
        "atendimentosHoje": contagem,
        "ganhosPrevistos": float(ganhos),
        "proximo_aniversariante": proximo_aniversariante
    }


# =========================================================
# CONFIGURAÇÕES DO LOJISTA (Integração WhatsApp / IA)
# =========================================================

class ConfiguracoesRequest(BaseModel):
    permitir_sobreposicao: bool
    horario_abertura: str   # HH:MM
    horario_fechamento: str # HH:MM
    dias_fechados: str | None = None          # "0,6"
    horario_almoco_inicio: str | None = None  # HH:MM
    horario_almoco_fim: str | None = None     # HH:MM


@router.get("/configuracoes")
def obter_configuracoes(
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna as configurações de agendamento do lojista."""
    return {
        "status": "sucesso",
        "permitir_sobreposicao": bool(merchant.permitir_sobreposicao),
        "horario_abertura": merchant.horario_abertura or "08:00",
        "horario_fechamento": merchant.horario_fechamento or "18:00",
        "dias_fechados": merchant.dias_fechados,
        "horario_almoco_inicio": merchant.horario_almoco_inicio,
        "horario_almoco_fim": merchant.horario_almoco_fim,
    }


@router.put("/configuracoes")
def atualizar_configuracoes(
    body: ConfiguracoesRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Atualiza as configurações de agendamento do lojista."""
    # Valida formato e valores das horas
    try:
        datetime.strptime(body.horario_abertura, "%H:%M")
        datetime.strptime(body.horario_fechamento, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Horários devem estar no formato HH:MM com valores válidos (ex: 08:00, 18:30).")

    merchant.permitir_sobreposicao = body.permitir_sobreposicao  # type: ignore
    merchant.horario_abertura = body.horario_abertura  # type: ignore
    merchant.horario_fechamento = body.horario_fechamento  # type: ignore
    merchant.dias_fechados = body.dias_fechados  # type: ignore
    merchant.horario_almoco_inicio = body.horario_almoco_inicio  # type: ignore
    merchant.horario_almoco_fim = body.horario_almoco_fim  # type: ignore

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    logger.info("Configuracoes atualizadas pelo lojista %s", merchant.id)
    return {"status": "sucesso", "mensagem": "Configurações salvas."}
# =========================================================
# BLOQUEAR HORÁRIO DA AGENDA
# =========================================================

class BloqueioRequest(BaseModel):
    data: str           # YYYY-MM-DD
    hora_inicio: str    # HH:MM
    hora_fim: str       # HH:MM
    motivo: str | None = "Bloqueio manual"

@router.post("/agendamentos/bloquear")
def bloquear_horario(
    body: BloqueioRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Insere um bloqueio na agenda criando um agendamento fictício com status 'bloqueado'."""
    try:
        data_obj = datetime.strptime(body.data, "%Y-%m-%d").date()
        inicio_obj = datetime.strptime(body.hora_inicio, "%H:%M")
        fim_obj = datetime.strptime(body.hora_fim, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data ou hora inválido.")

    duracao = int((fim_obj - inicio_obj).total_seconds() / 60)
    if duracao <= 0:
        raise HTTPException(status_code=400, detail="A hora de fim deve ser maior que a hora de início.")

    # Busca ou cria um customer padrão para bloqueio
    c_id = db.execute(
        text("SELECT id FROM customers WHERE telefone_whatsapp = '00000000000'"),
    ).scalar()

    if not c_id:
        c_id = db.execute(
            text("""
                INSERT INTO customers (nome, telefone_whatsapp)
                VALUES ('Bloqueio de Agenda', '00000000000')
                RETURNING id
            """)
        ).scalar()

    # Cria ou busca um serviço de Bloqueio com a duração exata
    nome_servico_bloqueio = f"Bloqueio {duracao} min"
    s_id = db.execute(
        text("SELECT id FROM services WHERE nome = :nome"),
        {"nome": nome_servico_bloqueio}
    ).scalar()

    if not s_id:
        s_id = db.execute(
            text("""
                INSERT INTO services (nome, preco, duracao_minutos)
                VALUES (:nome, 0, :dur)
                RETURNING id
            """),
            {"nome": nome_servico_bloqueio, "dur": duracao}
        ).scalar()

    max_ticket = db.execute(
        text("SELECT COALESCE(MAX(numero_ticket), 0) FROM appointments")
    ).scalar() or 0

    db.execute(
        text("""
            INSERT INTO appointments
                (customer_id, service_id, data_agendamento, horario_agendamento,
                 status, origem, numero_ticket, motivo_cancelamento)
            VALUES
                (:c_id, :s_id, :data, :hora, 'bloqueado', 'manual', :numero_ticket, :motivo)
        """),
        {
            "c_id": c_id,
            "s_id": s_id,
            "data": str(data_obj),
            "hora": body.hora_inicio,
            "numero_ticket": max_ticket + 1,
            "motivo": body.motivo
        }
    )
    db.commit()
    background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))
    
    return {"status": "sucesso", "mensagem": "Horário bloqueado com sucesso."}

@router.get("/agendamentos/bloqueios")
def listar_bloqueios(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Lista todos os bloqueios manuais futuros."""
    try:
        bloqueios = db.execute(text("""
            SELECT a.id, a.data_agendamento, a.horario_agendamento, a.motivo_cancelamento as motivo, s.duracao_minutos
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            WHERE a.status = 'bloqueado' 
              AND a.origem = 'manual'
              AND a.data_agendamento >= CURRENT_DATE
            ORDER BY a.data_agendamento ASC, a.horario_agendamento ASC
        """)).mappings().fetchall()
        
        result = []
        for b in bloqueios:
            hora_str = str(b["horario_agendamento"])
            if len(hora_str) > 5:
                inicio_obj = datetime.strptime(hora_str, "%H:%M:%S")
            else:
                inicio_obj = datetime.strptime(hora_str, "%H:%M")
                
            dur_val = b["duracao_minutos"] or 30
            fim_obj = inicio_obj + timedelta(minutes=dur_val)
            
            result.append({
                "id": b["id"],
                "data": str(b["data_agendamento"]),
                "hora_inicio": inicio_obj.strftime("%H:%M"),
                "hora_fim": fim_obj.strftime("%H:%M"),
                "motivo": b["motivo"]
            })
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agendamentos/bloqueios/{bloqueio_id}")
def remover_bloqueio(
    bloqueio_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Remove um bloqueio manual."""
    try:
        res = db.execute(text("""
            DELETE FROM appointments 
            WHERE id = :id AND status = 'bloqueado' AND origem = 'manual'
        """), {"id": bloqueio_id})
        
        if getattr(res, "rowcount", 1) == 0:
            raise HTTPException(status_code=404, detail="Bloqueio não encontrado.")
            
        db.commit()
        background_tasks.add_task(_broadcast_refresh, str(merchant.nome_do_schema))
        return {"status": "sucesso", "mensagem": "Bloqueio removido com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class ChangePasswordRequestMobile(BaseModel):
    nova_senha: str

@router.post("/auth/change-password")
def change_password_mobile(
    body: ChangePasswordRequestMobile,
    merchant: Merchant = Depends(get_lojista_atual)
):
    """Permite ao usuário logado alterar sua própria senha pelo app mobile."""
    from app.services.auth_service import hash_senha
    from app.database import SessionLocal
    
    with SessionLocal() as public_db:
        pub_merchant = public_db.query(Merchant).filter(Merchant.id == merchant.id).first()
        if pub_merchant:
            pub_merchant.senha_hash = hash_senha(body.nova_senha)
            public_db.commit()
            
    return {"status": "sucesso", "mensagem": "Senha alterada com sucesso!"}

# =========================================================
# CLIENTES (Listagem e Cadastro)
# =========================================================

@router.get("/clientes")
def listar_clientes(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual)
):
    """Retorna a lista de clientes cadastrados no schema do lojista."""
    query = text("""
        SELECT id, nome, telefone_whatsapp, ultima_interacao, data_nascimento, origem
        FROM customers
        ORDER BY nome ASC
    """)
    resultados = db.execute(query).mappings().all()
    clientes = [dict(row) for row in resultados]
    
    # Formata a data para JSON serializável
    for c in clientes:
        if c["ultima_interacao"]:
            c["ultima_interacao"] = str(c["ultima_interacao"])
            
    return {"status": "sucesso", "dados": clientes}

class ClienteRequest(BaseModel):
    nome: str
    telefone_whatsapp: str
    data_nascimento: str | None = None

@router.post("/clientes")
def cadastrar_cliente(
    body: ClienteRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual)
):
    """Cadastra ou atualiza um cliente manualmente."""
    try:
        # Tira caracteres indesejados do telefone (para garantir padrão)
        tel_limpo = ''.join(filter(str.isdigit, body.telefone_whatsapp))
        
        # Padronização de número brasileiro (se não tiver 55 na frente)
        if len(tel_limpo) in [10, 11] and not tel_limpo.startswith("55"):
            tel_limpo = "55" + tel_limpo
            
        result = db.execute(
            text("""
                INSERT INTO customers (nome, telefone_whatsapp, data_nascimento)
                VALUES (:nome, :tel, :dn)
                ON CONFLICT (telefone_whatsapp) DO UPDATE 
                    SET nome = EXCLUDED.nome, data_nascimento = COALESCE(EXCLUDED.data_nascimento, customers.data_nascimento)
                RETURNING id
            """),
            {"nome": body.nome, "tel": tel_limpo, "dn": body.data_nascimento}
        )
        db.commit()
        return {"status": "sucesso", "mensagem": "Cliente salvo com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/clientes/{cliente_id}")
def editar_cliente(
    cliente_id: int,
    body: ClienteRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual)
):
    """Edita as informações de um cliente existente."""
    try:
        tel_limpo = ''.join(filter(str.isdigit, body.telefone_whatsapp))
        if len(tel_limpo) in [10, 11] and not tel_limpo.startswith("55"):
            tel_limpo = "55" + tel_limpo
            
        result = db.execute(
            text("""
                UPDATE customers 
                SET nome = :nome, telefone_whatsapp = :tel, data_nascimento = :dn
                WHERE id = :id
            """),
            {"nome": body.nome, "tel": tel_limpo, "dn": body.data_nascimento, "id": cliente_id}
        )
        if getattr(result, "rowcount", 0) == 0:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
            
        db.commit()
        return {"status": "sucesso", "mensagem": "Cliente atualizado com sucesso!"}
    except Exception as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Este telefone já está cadastrado para outro cliente.")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clientes/{cliente_id}")
def excluir_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual)
):
    """Exclui um cliente existente."""
    try:
        # Verifica se o cliente tem agendamentos (opcional: ou deletar em cascata)
        # Vamos deletar os agendamentos associados ou apenas o cliente
        # Como o on delete cascade não está claro, vamos tentar apenas deletar o cliente
        # e se der erro de foreign key, avisamos.
        
        result = db.execute(
            text("DELETE FROM customers WHERE id = :id"),
            {"id": cliente_id}
        )
        if getattr(result, "rowcount", 0) == 0:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
            
        db.commit()
        return {"status": "sucesso", "mensagem": "Cliente excluído com sucesso!"}
    except Exception as e:
        db.rollback()
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Não é possível excluir este cliente pois ele possui agendamentos associados.")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# INSIGHTS DO CLIENTE (CRM)
# =========================================================

@router.get("/clientes/{cliente_id}/insights")
def obter_insights_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual)
):
    """
    Retorna os insights do cliente para o painel de CRM.
    - Dias desde a última visita
    - Serviço mais agendado
    - Total gasto (Lifetime Value)
    """
    try:
        # 1. Serviço mais agendado e Total Gasto
        query_stats = text("""
            SELECT 
                s.nome as servico_favorito,
                COUNT(a.id) as qtd_servico,
                SUM(
                    CASE
                        WHEN COALESCE(a.is_paid_in_package, false) = true THEN 0
                        WHEN a.valor_cobrado IS NOT NULL THEN a.valor_cobrado
                        ELSE COALESCE(s.preco, 0)
                    END
                ) as total_gasto
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            WHERE a.customer_id = :cliente_id
              AND a.status IN ('concluido', 'aprovado', 'confirmado')
            GROUP BY s.id, s.nome
            ORDER BY qtd_servico DESC
        """)
        stats_rows = db.execute(query_stats, {"cliente_id": cliente_id}).mappings().all()
        
        servico_favorito = "Nenhum"
        total_gasto = 0.0
        
        if stats_rows:
            servico_favorito = stats_rows[0]["servico_favorito"] or "Desconhecido"
            # Soma o total_gasto de TODOS os serviços
            total_gasto = sum([float(r["total_gasto"] or 0) for r in stats_rows])

        # 2. Última visita
        query_ultima = text("""
            SELECT MAX(data_agendamento) as ultima_visita
            FROM appointments
            WHERE customer_id = :cliente_id
              AND status IN ('concluido', 'aprovado', 'confirmado')
              AND data_agendamento <= CURRENT_DATE
        """)
        ultima_row = db.execute(query_ultima, {"cliente_id": cliente_id}).mappings().first()
        
        dias_sem_visita = None
        if ultima_row and ultima_row["ultima_visita"]:
            delta = date.today() - ultima_row["ultima_visita"]
            dias_sem_visita = delta.days
            
        return {
            "status": "sucesso",
            "dias_desde_ultimo_agendamento": dias_sem_visita,
            "servico_mais_agendado": servico_favorito,
            "total_gasto": total_gasto
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
