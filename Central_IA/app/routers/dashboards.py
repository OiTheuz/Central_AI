# ============================================================
# Router de Dashboards — Métricas agregadas para o App Lojista
# Todas as rotas usam o schema do lojista autenticado via JWT
# ============================================================

import logging
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.dependencies import get_db
from app.models import Merchant
from app.services.auth_service import get_lojista_atual

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/dashboards",
    tags=["Dashboards"],
)

# Status que representam agendamentos efetivos (atendidos ou confirmados)
# Exclui: 'pendente', 'cancelado', 'recusado'
_STATUS_EFETIVOS = "('concluido', 'aprovado', 'confirmado')"


# ─── Helpers ─────────────────────────────────────────────────

def _parse_datas(data_inicio: str, data_fim: str) -> tuple[date, date]:
    """Valida e converte parâmetros de data."""
    try:
        di = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        df = datetime.strptime(data_fim, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Datas devem estar no formato YYYY-MM-DD.")
    if di > df:
        raise HTTPException(status_code=400, detail="data_inicio não pode ser maior que data_fim.")
    return di, df


# =========================================================
# 1. FATURAMENTO REALIZADO (gráfico de barras por dia)
# =========================================================

@router.get("/faturamento")
def obter_faturamento(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Retorna faturamento realizado por dia (agendamentos efetivos).
    Usa valor_cobrado quando presente, senão usa services.preco.
    Ignora sessões marcadas como is_paid_in_package = true.
    """
    di, df = _parse_datas(data_inicio, data_fim)

    query = text(f"""
        SELECT
            a.data_agendamento AS data,
            COALESCE(
                SUM(
                    CASE
                        WHEN COALESCE(a.is_paid_in_package, false) = true THEN 0
                        WHEN a.valor_cobrado IS NOT NULL THEN a.valor_cobrado
                        ELSE COALESCE(s.preco, 0)
                    END
                ),
                0
            ) AS total
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status IN {_STATUS_EFETIVOS}
          AND a.data_agendamento BETWEEN :di AND :df
        GROUP BY a.data_agendamento
        ORDER BY a.data_agendamento
    """)

    rows = db.execute(query, {"di": di, "df": df}).mappings().all()
    dados = [{"data": str(r["data"]), "total": float(r["total"])} for r in rows]

    return {"status": "sucesso", "dados": dados}


# =========================================================
# 2. PREVISÃO DE CAIXA (KPI)
# =========================================================

@router.get("/previsao-caixa")
def obter_previsao_caixa(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Soma o valor financeiro de todos os agendamentos futuros
    que não estejam cancelados/recusados.
    """
    hoje = date.today()

    query = text("""
        SELECT COALESCE(
            SUM(
                CASE
                    WHEN COALESCE(a.is_paid_in_package, false) = true THEN 0
                    WHEN a.valor_cobrado IS NOT NULL THEN a.valor_cobrado
                    ELSE COALESCE(s.preco, 0)
                END
            ),
            0
        ) AS total
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.data_agendamento >= :hoje
          AND a.status NOT IN ('cancelado', 'recusado')
    """)

    total = db.execute(query, {"hoje": hoje}).scalar() or 0

    return {"status": "sucesso", "previsao": float(total)}


# =========================================================
# 3. TICKET MÉDIO (KPI)
# =========================================================

@router.get("/ticket-medio")
def obter_ticket_medio(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Faturamento Total / Quantidade de Agendamentos efetivos no período."""
    di, df = _parse_datas(data_inicio, data_fim)

    query = text(f"""
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN COALESCE(a.is_paid_in_package, false) = true THEN 0
                        WHEN a.valor_cobrado IS NOT NULL THEN a.valor_cobrado
                        ELSE COALESCE(s.preco, 0)
                    END
                ),
                0
            ) AS faturamento,
            COUNT(*) AS total_concluidos
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status IN {_STATUS_EFETIVOS}
          AND a.data_agendamento BETWEEN :di AND :df
    """)

    row = db.execute(query, {"di": di, "df": df}).mappings().first()
    faturamento = float(row["faturamento"]) if row else 0
    total = int(row["total_concluidos"]) if row else 0
    ticket = round(faturamento / total, 2) if total > 0 else 0

    return {
        "status": "sucesso",
        "ticket_medio": ticket,
        "faturamento": faturamento,
        "total_concluidos": total,
    }


# =========================================================
# 4. SERVIÇOS CAMPEÕES (Donut / Pizza)
# =========================================================

@router.get("/servicos-campeoes")
def obter_servicos_campeoes(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Volumetria de cada serviço prestado (efetivos) no período."""
    di, df = _parse_datas(data_inicio, data_fim)

    query = text(f"""
        SELECT
            COALESCE(s.nome, 'Sem serviço') AS servico,
            COUNT(*) AS quantidade
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status IN {_STATUS_EFETIVOS}
          AND a.data_agendamento BETWEEN :di AND :df
        GROUP BY s.nome
        ORDER BY quantidade DESC
        LIMIT 10
    """)

    rows = db.execute(query, {"di": di, "df": df}).mappings().all()
    dados = [{"servico": r["servico"], "quantidade": int(r["quantidade"])} for r in rows]

    return {"status": "sucesso", "dados": dados}


# =========================================================
# 5. NOVOS vs. RECORRENTES
# =========================================================

@router.get("/novos-vs-recorrentes")
def obter_novos_vs_recorrentes(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Para cada agendamento efetivo no período, verifica se o cliente
    já tinha um agendamento anterior a data_inicio → Recorrente.
    Se não → Novo.
    Agrupa por semana para o Stacked Bar chart.
    """
    di, df = _parse_datas(data_inicio, data_fim)

    query = text(f"""
        WITH agendamentos_periodo AS (
            SELECT
                a.id,
                a.customer_id,
                a.data_agendamento,
                CASE
                    WHEN EXISTS (
                        SELECT 1 FROM appointments prev
                        WHERE prev.customer_id = a.customer_id
                          AND prev.status IN {_STATUS_EFETIVOS}
                          AND prev.data_agendamento < :di
                    ) THEN 'recorrente'
                    ELSE 'novo'
                END AS tipo_cliente
            FROM appointments a
            WHERE a.status IN {_STATUS_EFETIVOS}
              AND a.data_agendamento BETWEEN :di AND :df
        )
        SELECT
            DATE_TRUNC('week', data_agendamento)::date AS semana,
            tipo_cliente,
            COUNT(*) AS quantidade
        FROM agendamentos_periodo
        GROUP BY semana, tipo_cliente
        ORDER BY semana
    """)

    rows = db.execute(query, {"di": di, "df": df}).mappings().all()

    # Agrupa por semana
    semanas: dict[str, dict] = {}
    for r in rows:
        s = str(r["semana"])
        if s not in semanas:
            semanas[s] = {"semana": s, "novos": 0, "recorrentes": 0}
        if r["tipo_cliente"] == "novo":
            semanas[s]["novos"] = int(r["quantidade"])
        else:
            semanas[s]["recorrentes"] = int(r["quantidade"])

    dados = list(semanas.values())
    return {"status": "sucesso", "dados": dados}


# =========================================================
# 6. RANKING VIP (Top 5 clientes)
# =========================================================

@router.get("/ranking-vip")
def obter_ranking_vip(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Top 5 clientes por faturamento no período."""
    di, df = _parse_datas(data_inicio, data_fim)

    query = text(f"""
        SELECT
            c.nome AS cliente,
            c.telefone_whatsapp AS telefone,
            COUNT(a.id) AS total_agendamentos,
            COALESCE(
                SUM(
                    CASE
                        WHEN COALESCE(a.is_paid_in_package, false) = true THEN 0
                        WHEN a.valor_cobrado IS NOT NULL THEN a.valor_cobrado
                        ELSE COALESCE(s.preco, 0)
                    END
                ),
                0
            ) AS faturamento
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status IN {_STATUS_EFETIVOS}
          AND a.data_agendamento BETWEEN :di AND :df
        GROUP BY c.id, c.nome, c.telefone_whatsapp
        ORDER BY faturamento DESC
        LIMIT 5
    """)

    rows = db.execute(query, {"di": di, "df": df}).mappings().all()
    dados = [
        {
            "posicao": i + 1,
            "cliente": r["cliente"] or "Cliente",
            "telefone": r["telefone"] or "",
            "total_agendamentos": int(r["total_agendamentos"]),
            "faturamento": float(r["faturamento"]),
        }
        for i, r in enumerate(rows)
    ]

    return {"status": "sucesso", "dados": dados}


# =========================================================
# 7. ALERTA DE "SUMIDOS" (clientes inativos há 45+ dias)
# =========================================================

@router.get("/clientes-sumidos")
def obter_clientes_sumidos(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Clientes cujo último agendamento efetivo ocorreu há mais de 45 dias.
    """
    limite = date.today() - timedelta(days=45)

    query = text(f"""
        SELECT
            c.nome AS cliente,
            c.telefone_whatsapp AS telefone,
            MAX(a.data_agendamento) AS ultimo_agendamento
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE a.status IN {_STATUS_EFETIVOS}
        GROUP BY c.id, c.nome, c.telefone_whatsapp
        HAVING MAX(a.data_agendamento) < :limite
        ORDER BY ultimo_agendamento ASC
        LIMIT 20
    """)

    rows = db.execute(query, {"limite": limite}).mappings().all()
    hoje = date.today()
    dados = [
        {
            "cliente": r["cliente"] or "Cliente",
            "telefone": r["telefone"] or "",
            "ultimo_agendamento": str(r["ultimo_agendamento"]),
            "dias_ausente": (hoje - r["ultimo_agendamento"]).days,
        }
        for r in rows
    ]

    return {"status": "sucesso", "dados": dados}


# =========================================================
# 8. FATURAMENTO VS CUSTOS
# =========================================================

@router.get("/faturamento-vs-custos")
def obter_faturamento_vs_custos(
    meses: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Retorna o faturamento e os gastos agrupados por mês (últimos N meses).
    """
    hoje = date.today()
    # Aproximação para pegar meses atrás (dia 1)
    inicio = (hoje.replace(day=1) - timedelta(days=30*meses)).replace(day=1)

    # Buscar Faturamento
    query_fat = text(f"""
        SELECT 
            TO_CHAR(DATE_TRUNC('month', a.data_agendamento), 'MM/YYYY') AS mes_ano,
            DATE_TRUNC('month', a.data_agendamento) AS mes_data,
            COALESCE(
                SUM(
                    CASE
                        WHEN COALESCE(a.is_paid_in_package, false) = true THEN 0
                        WHEN a.valor_cobrado IS NOT NULL THEN a.valor_cobrado
                        ELSE COALESCE(s.preco, 0)
                    END
                ),
                0
            ) AS faturamento
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status IN {_STATUS_EFETIVOS}
          AND a.data_agendamento >= :inicio
        GROUP BY mes_ano, mes_data
    """)
    fat_rows = db.execute(query_fat, {"inicio": inicio}).mappings().all()
    fat_dict = {r["mes_ano"]: float(r["faturamento"]) for r in fat_rows}
    
    # Buscar Custos
    query_custos = text("""
        SELECT 
            TO_CHAR(DATE_TRUNC('month', data), 'MM/YYYY') AS mes_ano,
            DATE_TRUNC('month', data) AS mes_data,
            COALESCE(SUM(valor), 0) AS custos
        FROM custos
        WHERE data >= :inicio
        GROUP BY mes_ano, mes_data
    """)
    custos_rows = db.execute(query_custos, {"inicio": inicio}).mappings().all()
    custos_dict = {r["mes_ano"]: float(r["custos"]) for r in custos_rows}

    # Mesclar e ordenar
    meses_set = set(fat_dict.keys()).union(set(custos_dict.keys()))
    
    def sort_key(ma):
        m, y = ma.split('/')
        return int(y) * 100 + int(m)
        
    meses_ordenados = sorted(list(meses_set), key=sort_key)
    
    dados = []
    for ma in meses_ordenados:
        dados.append({
            "label": ma,
            "faturamento": fat_dict.get(ma, 0.0),
            "custos": custos_dict.get(ma, 0.0)
        })
        
    # Se não tiver dados, envia o mês atual zerado
    if not dados:
        ma = hoje.strftime("%m/%Y")
        dados.append({"label": ma, "faturamento": 0.0, "custos": 0.0})
        
    return {"status": "sucesso", "dados": dados}


# =========================================================
# 9. PRÓXIMOS ANIVERSARIANTES
# =========================================================

@router.get("/proximos-aniversariantes")
def obter_proximos_aniversariantes(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """
    Retorna os 3 próximos clientes a fazerem aniversário, 
    independentemente do filtro global de datas do dashboard.
    """
    query = text("""
        SELECT id, nome, data_nascimento, 
               (SUBSTRING(data_nascimento, 6, 5) = TO_CHAR(CURRENT_DATE, 'MM-DD')) as is_hoje
        FROM customers
        WHERE data_nascimento IS NOT NULL AND data_nascimento != '' AND LENGTH(data_nascimento) = 10
        ORDER BY
          SUBSTRING(data_nascimento, 6, 5) < TO_CHAR(CURRENT_DATE, 'MM-DD'),
          SUBSTRING(data_nascimento, 6, 5)
        LIMIT 3
    """)

    rows = db.execute(query).mappings().all()
    
    dados = []
    for r in rows:
        dados.append({
            "id": r["id"],
            "nome": r["nome"],
            "data_nascimento": r["data_nascimento"],
            "is_hoje": bool(r["is_hoje"])
        })

    return {"status": "sucesso", "dados": dados}
