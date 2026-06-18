
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

    # Busca ou cria um serviço padrão para bloqueio
    s_id = db.execute(
        text("SELECT id FROM services WHERE nome = 'Bloqueio'"),
    ).scalar()

    if not s_id:
        s_id = db.execute(
            text("""
                INSERT INTO services (nome, preco, duracao_minutos)
                VALUES ('Bloqueio', 0, 30)
                RETURNING id
            """)
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
