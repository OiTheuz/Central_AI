from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class Professional(Base):
    """
    Representa um profissional dentro do schema do lojista.
    Será criado dinamicamente em schema_XYZ.professionals
    """
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)


class ProfessionalShift(Base):
    """
    Representa os horários de trabalho de um profissional.
    Será criado dinamicamente em schema_XYZ.professional_shifts
    """
    __tablename__ = "professional_shifts"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False)
    dia_semana = Column(Integer, nullable=False) # 0 = Segunda, 6 = Domingo
    turno_inicio = Column(String(5), nullable=True) # Ex: 08:00
    turno_fim = Column(String(5), nullable=True) # Ex: 18:00
    dia_fechado = Column(Boolean, default=False, nullable=False, server_default="false")
