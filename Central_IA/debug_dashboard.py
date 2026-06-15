from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("SET search_path TO jessiely_moura, public"))

    # Simula a query de faturamento do mês
    r = conn.execute(text("""
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
        WHERE a.status IN ('concluido', 'aprovado', 'confirmado')
          AND a.data_agendamento BETWEEN '2026-06-01' AND '2026-06-12'
        GROUP BY a.data_agendamento
        ORDER BY a.data_agendamento
    """))
    print("=== FATURAMENTO POR DIA (MÊS ATUAL) ===")
    for row in r:
        print(f"  {row[0]}: R$ {row[1]}")

    # Serviços campeões
    r2 = conn.execute(text("""
        SELECT COALESCE(s.nome, 'Sem serviço') AS servico, COUNT(*) AS quantidade
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status IN ('concluido', 'aprovado', 'confirmado')
          AND a.data_agendamento BETWEEN '2026-06-01' AND '2026-06-12'
        GROUP BY s.nome ORDER BY quantidade DESC
    """))
    print("\n=== SERVIÇOS CAMPEÕES ===")
    for row in r2:
        print(f"  {row[0]}: {row[1]}")

    # Ranking VIP
    r3 = conn.execute(text("""
        SELECT c.nome, COUNT(a.id) as total, COALESCE(SUM(COALESCE(s.preco, 0)), 0) as fat
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.status IN ('concluido', 'aprovado', 'confirmado')
          AND a.data_agendamento BETWEEN '2026-06-01' AND '2026-06-12'
        GROUP BY c.id, c.nome ORDER BY fat DESC LIMIT 5
    """))
    print("\n=== RANKING VIP ===")
    for row in r3:
        print(f"  {row[0]}: {row[1]} agendamentos, R$ {row[2]}")
