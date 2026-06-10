# ============================================================
# Router do App Lojista — Endpoints protegidos por JWT
# Todas as rotas usam o schema do lojista autenticado
# ============================================================

import logging
import re
import traceback
import uuid
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.dependencies import get_db
from app.database import validar_schema
from app.models import Merchant
from app.services.auth_service import get_lojista_atual
from app.services.whatsapp_service import enviar_mensagem_whatsapp

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/mobile",
    tags=["App Lojista"],
)


# ─── Helper: Serialização de agendamento ────────────────────

def _serializar_agendamento(row) -> dict:
    """Serializa uma row de agendamento para o formato JSON do app."""
    return {
        "id": row["id"],
        "clienteNome": row["cliente_nome"] or "Cliente",
        "clienteTelefone": row["cliente_telefone"] or "",
        "servico": row["servico"] or "Serviço não especificado",
        "data": str(row["data_agendamento"]),
        "hora": row["horario_agendamento"].strftime("%H:%M") if row["horario_agendamento"] else "--:--",
        "status": row["status"],
        "origem": (row["origem"] or "manual").lower(),
    }



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
            a.origem
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
            a.origem
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
            a.origem
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
            mensagem = "Seu agendamento foi confirmado pelo lojista! Te esperamos. Até logo! 👋"
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

            mensagem = (
                f"Infelizmente, o estabelecimento precisou recusar a sua solicitação{contexto}. "
                f"Mas você pode fazer um novo agendamento! "
                f"É só mandar um 'Oi' para recomeçarmos. 😊"
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


@router.post("/agendamentos/manual")
def criar_agendamento_manual(
    body: AgendamentoManualRequest,
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

        registros = [
            {
                "c_id": cliente_id,
                "s_id": body.servicoId,
                "data": str(d),
                "hora": body.hora,
                "rec_id": recurrence_id,
            }
            for d in datas
        ]

        db.execute(
            text("""
                INSERT INTO appointments
                    (customer_id, service_id, data_agendamento, horario_agendamento,
                     status, origem, recurrence_id)
                VALUES
                    (:c_id, :s_id, :data, :hora, 'aprovado', 'manual', :rec_id)
            """),
            registros,
        )
        db.commit()

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
        traceback.print_exc()
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

    return {
        "status": "sucesso",
        "atendimentosHoje": contagem,
        "ganhosPrevistos": float(ganhos),
    }


# =========================================================
# CONFIGURAÇÕES DO LOJISTA (Integração WhatsApp / IA)
# =========================================================

class ConfiguracoesRequest(BaseModel):
    permitir_sobreposicao: bool
    horario_abertura: str   # HH:MM
    horario_fechamento: str # HH:MM


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
    }


@router.put("/configuracoes")
def atualizar_configuracoes(
    body: ConfiguracoesRequest,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Atualiza as configurações de agendamento do lojista."""
    hora_re = re.compile(r'^\d{2}:\d{2}$')
    if not hora_re.match(body.horario_abertura) or not hora_re.match(body.horario_fechamento):
        raise HTTPException(status_code=400, detail="Horários devem estar no formato HH:MM.")

    merchant.permitir_sobreposicao = body.permitir_sobreposicao  # type: ignore
    merchant.horario_abertura = body.horario_abertura  # type: ignore
    merchant.horario_fechamento = body.horario_fechamento  # type: ignore
    db.commit()
    logger.info("Configuracoes atualizadas pelo lojista %s", merchant.id)
    return {"status": "sucesso", "mensagem": "Configurações salvas."}