from pydantic import BaseModel
from typing import Optional


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
