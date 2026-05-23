from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import text
from app.database import get_db # Confirme se o caminho para o seu get_db está correto

# Criamos um roteador específico para o aplicativo móvel
router = APIRouter(
    prefix="/api/mobile",
    tags=["App Lojista"]
)

@router.get("/agendamentos/hoje/{schema_lojista}")
def obter_agendamentos_hoje(schema_lojista: str, db: Session = Depends(get_db)):
    """
    Esta rota busca todos os agendamentos do dia atual para um lojista específico.
    O telemóvel vai chamar isto assim que a app abrir.
    """
    try:
        # Procuramos os agendamentos de HOJE no schema daquele lojista (ex: moura_schema)
        query = text(f"""
            SELECT id, customer_id, servico, data_agendamento, hora_agendamento 
            FROM {schema_lojista}.appointments 
            WHERE data_agendamento = :hoje
            ORDER BY hora_agendamento ASC
        """)
        
        # O Python pergunta ao PostgreSQL
        resultados = db.execute(query, {"hoje": date.today()}).fetchall()
        
        # Preparamos a "caixinha" (JSON) para devolver ao telemóvel
        agendamentos = []
        for row in resultados:
            agendamentos.append({
                "id": row.id,
                "cliente_id": row.customer_id,
                "servico": row.servico,
                "data": str(row.data_agendamento),
                "hora": str(row.hora_agendamento)
            })
            
        return {"status": "sucesso", "total": len(agendamentos), "dados": agendamentos}
    
    except Exception as e:
        # Se algo falhar no banco de dados, avisamos o telemóvel
        raise HTTPException(status_code=500, detail=f"Erro ao buscar agenda: {str(e)}")