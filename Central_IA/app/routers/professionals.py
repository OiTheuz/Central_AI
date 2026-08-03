from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.database import get_public_db
from app.models.merchant import Merchant
from app.services.auth_service import get_lojista_atual
from app.models.professional import Professional, ProfessionalShift

router = APIRouter(
    prefix="/api/professionals",
    tags=["Professionals"],
)

class ShiftEntry(BaseModel):
    dia_semana: int
    turno_inicio: str = None
    turno_fim: str = None
    dia_fechado: bool = False

class ShiftsRequest(BaseModel):
    turnos: List[ShiftEntry]

@router.put("/{prof_id}/shifts")
def save_professional_shifts(
    prof_id: int, 
    body: ShiftsRequest, 
    db: Session = Depends(get_public_db), 
    merchant: Merchant = Depends(get_lojista_atual)
):
    """
    Salva os turnos de trabalho para um profissional específico.
    """
    db.execute(text(f"SET search_path TO {merchant.nome_do_schema}"))
    
    # Valida se o profissional existe
    prof = db.query(Professional).filter(Professional.id == prof_id).first()
    if not prof:
        db.execute(text("SET search_path TO public"))
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")
        
    # Limpa os turnos antigos deste profissional
    db.query(ProfessionalShift).filter(ProfessionalShift.professional_id == prof_id).delete()
    
    # Adiciona os novos
    for t in body.turnos:
        shift = ProfessionalShift(
            professional_id=prof_id,
            dia_semana=t.dia_semana,
            turno_inicio=t.turno_inicio,
            turno_fim=t.turno_fim,
            dia_fechado=t.dia_fechado
        )
        db.add(shift)
        
    db.commit()
    db.execute(text("SET search_path TO public"))
    
    return {"status": "sucesso", "mensagem": "Turnos salvos com sucesso."}
