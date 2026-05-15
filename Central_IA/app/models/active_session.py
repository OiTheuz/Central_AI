from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func

from app.database import Base


class ActiveSession(Base):
    __tablename__ = "active_sessions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    telefone_cliente = Column(String, nullable=False)
    loja_atual = Column(String, nullable=False)
    dados_sessao = Column(JSON, nullable=True)
    ativo = Column(Boolean, default=True)
    ultima_interacao = Column(DateTime, server_default=func.now(), onupdate=func.now())
