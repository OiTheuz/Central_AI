from sqlalchemy.orm import Session

from app.models.active_session import ActiveSession

# =========================================================
# FUNÇÕES DE MEMÓRIA DO BOT (Sessões ativas por cliente)

def get_sessao_cliente(db: Session, telefone: str):
    return db.query(ActiveSession).filter(
        ActiveSession.telefone_cliente == telefone
    ).first()


def salvar_sessao_cliente(db: Session, telefone: str, schema_loja: str):
    sessao = get_sessao_cliente(db, telefone)
    if sessao:
        sessao.loja_atual = schema_loja
    else:
        nova_sessao = ActiveSession(telefone_cliente=telefone, loja_atual=schema_loja)
        db.add(nova_sessao)
    db.commit()


def deletar_sessao_cliente(db: Session, telefone: str):
    db.query(ActiveSession).filter(
        ActiveSession.telefone_cliente == telefone
    ).delete()
    db.commit()
