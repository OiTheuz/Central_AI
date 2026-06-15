import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date

from app.dependencies import get_db
from app.models import Merchant
from app.services.auth_service import get_lojista_atual
from app.schemas.custo import (
    CategoriaCustoCreate,
    CategoriaCustoResponse,
    CustoCreate,
    CustoResponse,
    CategoriaComCustos
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/mobile/custos",
    tags=["Custos"],
)

# =========================================================
# CATEGORIAS DE CUSTO
# =========================================================

@router.get("/categorias", response_model=List[CategoriaCustoResponse])
def listar_categorias(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    query = text("SELECT * FROM categorias_custo ORDER BY nome")
    rows = db.execute(query).mappings().all()
    return rows

@router.post("/categorias", response_model=CategoriaCustoResponse)
def criar_categoria(
    categoria: CategoriaCustoCreate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    query = text("""
        INSERT INTO categorias_custo (nome) 
        VALUES (:nome) 
        RETURNING *
    """)
    row = db.execute(query, {"nome": categoria.nome}).mappings().first()
    db.commit()
    return row


# =========================================================
# CUSTOS (DESPESAS)
# =========================================================

@router.get("", response_model=List[CustoResponse])
def listar_custos(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    if mes and ano:
        query = text("""
            SELECT * FROM custos 
            WHERE EXTRACT(MONTH FROM data) = :mes 
              AND EXTRACT(YEAR FROM data) = :ano
            ORDER BY data DESC, id DESC
        """)
        rows = db.execute(query, {"mes": mes, "ano": ano}).mappings().all()
    else:
        query = text("SELECT * FROM custos ORDER BY data DESC, id DESC LIMIT 100")
        rows = db.execute(query).mappings().all()
        
    return rows

@router.post("", response_model=CustoResponse)
def registrar_custo(
    custo: CustoCreate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    query = text("""
        INSERT INTO custos (categoria_id, valor, data, descricao) 
        VALUES (:categoria_id, :valor, :data, :descricao) 
        RETURNING *
    """)
    params = {
        "categoria_id": custo.categoria_id,
        "valor": custo.valor,
        "data": custo.data or date.today(),
        "descricao": custo.descricao,
    }
    try:
        row = db.execute(query, params).mappings().first()
        db.commit()
        return row
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/por-categoria", response_model=List[CategoriaComCustos])
def listar_custos_agrupados(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_lojista_atual),
):
    """Retorna as categorias e todos os custos dentro delas no mês/ano"""
    
    cat_query = text("SELECT * FROM categorias_custo ORDER BY nome")
    categorias = db.execute(cat_query).mappings().all()
    
    if mes and ano:
        custo_query = text("""
            SELECT * FROM custos 
            WHERE EXTRACT(MONTH FROM data) = :mes AND EXTRACT(YEAR FROM data) = :ano
            ORDER BY data DESC
        """)
        custos = db.execute(custo_query, {"mes": mes, "ano": ano}).mappings().all()
    else:
        custo_query = text("SELECT * FROM custos ORDER BY data DESC LIMIT 500")
        custos = db.execute(custo_query).mappings().all()
        
    resultado = []
    for cat in categorias:
        cat_dict = dict(cat)
        cat_dict["custos"] = [dict(c) for c in custos if c["categoria_id"] == cat["id"]]
        # Só retorna categorias que tem custos ou se for recente (se quiser)
        # Vamos retornar todas para poder ver as vazias também
        resultado.append(cat_dict)
        
    return resultado
