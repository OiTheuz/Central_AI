import sys
import os
import logging
from typing import Optional

# Adiciona o diretório raiz do projeto ao PYTHONPATH para permitir importação do pacote "app"
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import text
from app.database import SessionLocal
from app.models.merchant import Merchant

logger = logging.getLogger(__name__)

def criar_merchant(
    nome_loja: str,
    nome_schema: str,
    codigo_loja: Optional[str] = None,
    telefone: Optional[str] = None,
) -> Merchant:
    """Insere ou garante a existência de um Merchant.

    - ``nome_loja``: nome amigável usado pela UI (ex.: "jessiely").
    - ``nome_schema``: nome real do schema no PostgreSQL (ex.: "Jessiely_Moura").
    - ``codigo_loja``: código interno opcional; se ``None`` usa ``nome_schema``.
    - ``telefone``: contato opcional.
    """
    with SessionLocal() as db:
        # Verifica se já existe
        existente = db.execute(
            text(
                "SELECT id FROM merchant WHERE nome_do_schema = :schema OR nome_loja = :nome"
            ),
            {"schema": nome_schema, "nome": nome_loja},
        ).fetchone()

        if existente:
            logger.info("Merchant já existente: %s (%s)", nome_loja, nome_schema)
            return (
                db.query(Merchant)
                .filter(Merchant.id == existente[0])
                .first()
            )

        novo = Merchant(
            nome_loja=nome_loja,
            nome_do_schema=nome_schema,
            codigo_loja=codigo_loja or nome_schema,
            telefone_contato=telefone,
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        logger.info("Merchant criado: %s => schema %s", nome_loja, nome_schema)
        return novo

if __name__ == "__main__":
    # Inserir os merchants solicitados
    criar_merchant(nome_loja="jessiely", nome_schema="Jessiely_Moura")
    criar_merchant(nome_loja="Jessiely Moura", nome_schema="Jessiely_Moura")
    print("Merchants criados/confirmados.")
