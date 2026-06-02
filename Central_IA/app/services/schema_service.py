import logging
from typing import List

from sqlalchemy import text

from app.database import engine, validar_schema

logger = logging.getLogger(__name__)


def criar_novo_estabelecimento(schema_nome: str, tabelas: List[str]) -> None:
    """Cria um novo schema que representa um estabelecimento e copia a
    estrutura (sem dados) das tabelas informadas a partir do schema base
    `moura_schema`.

    Args:
        schema_nome: Nome do novo schema (deve ser validado).
        tabelas: Lista de nomes de tabelas a serem replicadas.
    """
    schema = validar_schema(schema_nome)
    try:
        with engine.begin() as conn:
            # Cria o schema se ainda não existir
            logger.info("Criando schema %s", schema)
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            # Copia a estrutura de cada tabela usando LIKE
            for tabela in tabelas:
                logger.info(
                    "Copiando estrutura da tabela %s para %s.%s",
                    tabela,
                    schema,
                    tabela,
                )
                conn.execute(
                    text(
                        f"CREATE TABLE {schema}.{tabela} (LIKE moura_schema.{tabela} INCLUDING ALL)"
                    )
                )
                conn.execute(text(f"TRUNCATE {schema}.{tabela}"))
        logger.info("Schema %s criado com %d tabelas", schema, len(tabelas))
    except Exception as e:
        logger.error("Falha ao criar schema %s: %s", schema, e)
        raise


def listar_schemas() -> List[str]:
    """Retorna a lista de schemas existentes no banco (exceto os padrões)."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'public')"
        ))
        return [row[0] for row in result.fetchall()]
