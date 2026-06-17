from pydantic import BaseModel
from typing import Optional


class MerchantBase(BaseModel):
    nome_loja: str
    codigo_loja: str
    telefone_contato: Optional[str] = None
    numero_whatsapp: Optional[str] = None
    nome_do_schema: str
    area_atuacao: Optional[str] = None


class MerchantCreate(MerchantBase):
    email: str
    senha: str
    is_admin: bool = False
    tem_dashboard: bool = False


class MerchantUpdate(BaseModel):
    """Schema para editar permissões de um lojista existente."""
    tem_dashboard: Optional[bool] = None
    is_admin: Optional[bool] = None
    area_atuacao: Optional[str] = None
    telefone_contato: Optional[str] = None
    numero_whatsapp: Optional[str] = None


class MerchantResponse(MerchantBase):
    id: int
    is_admin: bool
    tem_dashboard: bool
    email: Optional[str] = None
    push_token: Optional[str] = None

    class Config:
        from_attributes = True
