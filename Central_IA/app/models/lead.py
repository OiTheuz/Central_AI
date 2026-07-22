from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Lead(Base):
    __tablename__ = "lead"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=True)
    telefone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    nicho = Column(String, nullable=True)
    como_conheceu = Column(String, nullable=True)
    
    # Marcador para saber se o lead concluiu o Step 1 (virou Lojista)
    convertido = Column(Integer, default=0) # 0 = Não, 1 = Sim
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
