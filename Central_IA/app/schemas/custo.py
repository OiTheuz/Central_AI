from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class CategoriaCustoBase(BaseModel):
    nome: str

class CategoriaCustoCreate(CategoriaCustoBase):
    pass

class CategoriaCustoResponse(CategoriaCustoBase):
    id: int
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CustoBase(BaseModel):
    categoria_id: int
    valor: float
    data: Optional[date] = None
    descricao: Optional[str] = None

class CustoCreate(CustoBase):
    pass

class CustoResponse(CustoBase):
    id: int
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CategoriaComCustos(CategoriaCustoResponse):
    custos: List[CustoResponse] = []
    
class FaturamentoVsCusto(BaseModel):
    label: str # ex: "01/10", "Semana 1"
    faturamento: float
    custos: float
