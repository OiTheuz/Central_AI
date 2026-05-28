# ============================================================
# Router do App Lojista — Endpoints protegidos por JWT
# Todas as rotas usam o schema do lojista autenticado
# ============================================================

import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db, validar_schema
from app.models import Merchant
from app.services.auth_service import get_lojista_atual
from app.services.whatsapp_service import enviar_mensagem_whatsapp

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/mobile",
    tags=["App Lojista"],
)


# ─── Helper: SET search_path ────────────────────────────────

def _set_schema(db: Session, merchant: Merchant):
    """
    Define o search_path para o schema do lojista autenticado.
    Valida o nome do schema antes de interpolá-lo (anti SQL Injection).
    """
    schema = validar_schema(str(merchant.nome_do_schema))
    # Inclui 'public' para que queries ORM em tabelas do schema público
    # (ex: merchant) continuem funcionando na mesma sessão.
    db.execute(text(f"SET search_path TO {schema}, public"))


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
    _set_schema(db, merchant)

    query = text("""
        SELECT 
            a.id, 
            c.nome AS cliente_nome,
            c.telefone_whatsapp AS cliente_telefone,
            s.nome AS servico, 
            a.data_agendamento, 
            a.horario_agendamento,
            a.status
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.data_agendamento = :hoje
          AND a.status IN ('aprovado', 'confirmado')
        ORDER BY a.horario_agendamento ASC
        LIMIT 200
    """)

    resultados = db.execute(query, {"hoje": date.today()}).mappings().all()

    agendamentos = []
    for row in resultados:
        agendamentos.append({
            "id": row["id"],
            "clienteNome": row["cliente_nome"] or "Cliente",
            "clienteTelefone": row["cliente_telefone"] or "",
            "servico": row["servico"] or "Serviço não especificado",
            "data": str(row["data_agendamento"]),
            "hora": row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "--:--",
            "status": row["status"],
            "origem": "whatsapp_lau",
        })

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
    _set_schema(db, merchant)

    offset = (page - 1) * size

    query = text("""
        SELECT 
            a.id,
            c.nome AS cliente_nome,
            c.telefone_whatsapp AS cliente_telefone,
            s.nome AS servico,
            a.data_agendamento,
            a.horario_agendamento,
            a.status
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status = 'pendente'
        ORDER BY a.data_agendamento ASC, a.horario_agendamento ASC
        LIMIT :size OFFSET :offset
    """)

    resultados = db.execute(query, {"size": size, "offset": offset}).mappings().all()

    agendamentos = []
    for row in resultados:
        agendamentos.append({
            "id": row["id"],
            "clienteNome": row["cliente_nome"] or "Cliente",
            "clienteTelefone": row["cliente_telefone"] or "",
            "servico": row["servico"] or "Serviço não especificado",
            "data": str(row["data_agendamento"]),
            "hora": row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "--:--",
            "status": "pendente",
            "origem": "whatsapp_lau",
        })

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
    _set_schema(db, merchant)

    query = text("""
        SELECT 
            a.id,
            c.nome AS cliente_nome,
            c.telefone_whatsapp AS cliente_telefone,
            s.nome AS servico,
            a.data_agendamento,
            a.horario_agendamento,
            a.status
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.data_agendamento = :data
          AND a.status IN ('aprovado', 'confirmado', 'concluido')
        ORDER BY a.horario_agendamento ASC
        LIMIT 200
    """)

    resultados = db.execute(query, {"data": data}).mappings().all()

    agendamentos = []
    for row in resultados:
        agendamentos.append({
            "id": row["id"],
            "clienteNome": row["cliente_nome"] or "Cliente",
            "clienteTelefone": row["cliente_telefone"] or "",
            "servico": row["servico"] or "Serviço não especificado",
            "data": str(row["data_agendamento"]),
            "hora": row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "--:--",
            "status": row["status"],
            "origem": "whatsapp_lau",
        })

    return {"status": "sucesso", "total": len(agendamentos), "dados": agendamentos}


# =========================================================
# DATAS COM COMPROMISSOS (dots no calendário)
# =========================================================

@router.get("/agendamentos/datas-com-compromissos")
def obter_datas_com_compromissos(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna array de datas únicas que possuem agendamentos (aprovados/confirmados/concluidos)."""
    _set_schema(db, merchant)

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

@router.put("/agendamentos/{agendamento_id}/aprovar")
def aprovar_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Muda status do agendamento para 'aprovado' e envia mensagem
    de confirmação ao cliente via WhatsApp.
    """
    _set_schema(db, merchant)

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
    db.execute(
        text("UPDATE appointments SET status = 'aprovado' WHERE id = :id"),
        {"id": agendamento_id},
    )
    db.commit()
    logger.info("Agendamento %s aprovado pelo lojista %s", agendamento_id, merchant.id)

    # Enviar confirmação via WhatsApp ao cliente
    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            data_fmt = row["data_agendamento"].strftime("%d/%m/%Y") if row["data_agendamento"] else "data"
            hora_fmt = row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "horário"
            servico = row["servico_nome"] or "seu serviço"

            mensagem = (
                f"✅ Ótima notícia! Seu agendamento para {servico} "
                f"no dia {data_fmt} às {hora_fmt} foi confirmado "
                f"pela {merchant.nome_loja}! Te esperamos! 😊"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de aprovação: %s", e)

    return {"status": "sucesso", "mensagem": "Agendamento aprovado e cliente notificado!"}


# =========================================================
# RECUSAR AGENDAMENTO (pendente → recusado) + WhatsApp
# =========================================================

@router.put("/agendamentos/{agendamento_id}/recusar")
def recusar_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Muda status do agendamento para 'recusado' e envia mensagem
    de aviso ao cliente via WhatsApp.
    """
    _set_schema(db, merchant)

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
    db.execute(
        text("UPDATE appointments SET status = 'recusado' WHERE id = :id"),
        {"id": agendamento_id},
    )
    db.commit()
    logger.info("Agendamento %s recusado pelo lojista %s", agendamento_id, merchant.id)

    # Enviar aviso via WhatsApp ao cliente
    telefone = row["telefone_whatsapp"]
    if telefone:
        try:
            data_fmt = row["data_agendamento"].strftime("%d/%m/%Y") if row["data_agendamento"] else "data"
            hora_fmt = row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "horário"
            servico = row["servico_nome"] or "seu serviço"

            mensagem = (
                f"😔 Infelizmente, o horário para {servico} "
                f"no dia {data_fmt} às {hora_fmt} não está disponível "
                f"na {merchant.nome_loja}. Que tal escolher outro horário? "
                f"É só me mandar uma mensagem! 😊"
            )
            enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem)
        except Exception as e:
            logger.warning("Erro ao enviar WhatsApp de recusa: %s", e)

    return {"status": "sucesso", "mensagem": "Agendamento recusado e cliente notificado."}


# =========================================================
# SERVIÇOS DO LOJISTA
# =========================================================

@router.get("/servicos")
def obter_servicos(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Lista todos os serviços cadastrados no schema do lojista."""
    _set_schema(db, merchant)

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
    _set_schema(db, merchant)

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
    _set_schema(db, merchant)

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
    _set_schema(db, merchant)

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

class AgendamentoManualRequest(BaseModel):
    clienteNome: str
    clienteTelefone: str
    servicoId: int
    data: str   # YYYY-MM-DD
    hora: str   # HH:MM

@router.post("/agendamentos/manual")
def criar_agendamento_manual(
    body: AgendamentoManualRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Cria um agendamento manualmente pelo lojista (sem passar pelo WhatsApp)."""
    _set_schema(db, merchant)

    # Verificar se o serviço existe
    servico = db.execute(
        text("SELECT id, nome FROM services WHERE id = :sid"),
        {"sid": body.servicoId}
    ).mappings().fetchone()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")

    # Upsert do cliente pelo telefone
    db.execute(
        text("""
            INSERT INTO customers (nome, telefone_whatsapp)
            VALUES (:nome, :tel)
            ON CONFLICT (telefone_whatsapp) DO UPDATE SET nome = EXCLUDED.nome
        """),
        {"nome": body.clienteNome, "tel": body.clienteTelefone}
    )
    db.commit()

    cliente = db.execute(
        text("SELECT id FROM customers WHERE telefone_whatsapp = :tel"),
        {"tel": body.clienteTelefone}
    ).mappings().fetchone()

    if not cliente:
        raise HTTPException(status_code=500, detail="Falha ao localizar cliente após insert.")

    # Inserir agendamento com status 'aprovado' (criado pelo próprio lojista)
    db.execute(
        text("""
            INSERT INTO appointments (customer_id, service_id, data_agendamento, horario_agendamento, status)
            VALUES (:c_id, :s_id, :data, :hora, 'aprovado')
        """),
        {
            "c_id": cliente["id"],
            "s_id": body.servicoId,
            "data": body.data,
            "hora": body.hora,
        }
    )
    db.commit()

    logger.info(
        "Agendamento manual criado pelo lojista %s: %s em %s às %s",
        merchant.id, servico["nome"], body.data, body.hora
    )

    return {
        "status": "sucesso",
        "mensagem": f"Agendamento de {body.clienteNome} para {servico['nome']} criado com sucesso!"
    }


# =========================================================
# MÉTRICAS DE HOJE
# =========================================================

@router.get("/metricas/hoje")
def obter_metricas_hoje(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna contagem de atendimentos e ganhos previstos para hoje."""
    _set_schema(db, merchant)

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

    return {
        "status": "sucesso",
        "atendimentosHoje": contagem,
        "ganhosPrevistos": float(ganhos),
    }