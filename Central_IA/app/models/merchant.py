from sqlalchemy import Column, Integer, String

from app.database import Base


class Merchant(Base):
    __tablename__ = "merchant"

    id = Column(Integer, primary_key=True, index=True)
    nome_loja = Column(String(255), unique=True, nullable=False)
    codigo_loja = Column(String(50), unique=True, index=True)
    telefone_contato = Column(String(50))
    nome_do_schema = Column(String(50), unique=True, nullable=False)
    area_atuacao = Column(String(100))

    # Autenticação (login do lojista no app)
    email = Column(String(255), unique=True, nullable=True)
    senha_hash = Column(String(255), nullable=True)
    
    # Notificações Push
    push_token = Column(String(255), nullable=True)
