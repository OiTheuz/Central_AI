from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MerchantBase(BaseModel):
    nome_loja: str
    codigo_loja: str
    telefone_contato: Optional[str] = None
    nome_do_schema: str
    area_atuacao: Optional[str] = None

class MerchantCreate(MerchantBase):
    pass

class MerchantResponse(MerchantBase):
    id: int

    class Config:
        from_attributes = True

# NOVOS SCHEMAS PARA AGENDAMENTO
class AgendamentoCreate(BaseModel):
    codigo_loja: str  # Fundamental para a API saber em qual gaveta guardar!
    cliente_nome: str
    cliente_whatsapp: str
    data_horario: datetime
    servico: str