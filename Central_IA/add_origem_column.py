from app.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_db():
    with engine.connect() as conn:
        try:
            # Buscar todos os lojistas
            result = conn.execute(text("SELECT nome_do_schema FROM public.merchant"))
            schemas = [row[0] for row in result.fetchall()]
            
            for schema in schemas:
                # Validar o schema básico
                if not schema.isidentifier():
                    logger.warning(f"Schema inválido ignorado: {schema}")
                    continue
                
                try:
                    conn.execute(text(f"ALTER TABLE {schema}.appointments ADD COLUMN origem VARCHAR(50);"))
                    conn.commit()
                    logger.info(f"Coluna 'origem' adicionada no schema '{schema}'.")
                except Exception as e:
                    logger.info(f"Coluna 'origem' possivelmente já existe no schema '{schema}' ou erro: {e}")
                    conn.rollback() # Rollback the failed transaction block so we can continue
        
        except Exception as e:
            logger.error(f"Erro ao buscar schemas: {e}")

if __name__ == "__main__":
    update_db()
