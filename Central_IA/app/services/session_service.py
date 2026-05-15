from sqlalchemy.orm import Session

from app.models.active_session import ActiveSession

# =========================================================
# FUNÇÕES DE MEMÓRIA DO BOT (Sessões ativas por cliente)

def get_sessao_cliente(db: Session, telefone: str):
    return db.query(ActiveSession).filter(
        ActiveSession.telefone_cliente == telefone,
        ActiveSession.ativo == True
    ).first()


def salvar_sessao_cliente(db: Session, telefone: str, schema_loja: str, dados_sessao: dict = None):
    sessao = get_sessao_cliente(db, telefone)
    if sessao:
        sessao.loja_atual = schema_loja  # type: ignore[assignment]
        if dados_sessao is not None:
            sessao.dados_sessao = dados_sessao  # type: ignore[assignment]
    else:
        nova_sessao = ActiveSession(
            telefone_cliente=telefone, 
            loja_atual=schema_loja,
            dados_sessao=dados_sessao,
            ativo=True
        )
        db.add(nova_sessao)
    db.commit()


def encerrar_sessao_cliente(db: Session, telefone: str):
    sessao = get_sessao_cliente(db, telefone)
    if sessao:
        sessao.ativo = False  # type: ignore[assignment]
        db.commit()
