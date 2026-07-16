import logging
from typing import List

from sqlalchemy import text

from app.database import engine, validar_schema

logger = logging.getLogger(__name__)


def criar_novo_estabelecimento(schema_nome: str, tabelas: List[str], nicho: str = None) -> None:
    """Cria um novo schema que representa um estabelecimento e copia a
    estrutura das tabelas informadas a partir de um schema base.
    Se um nicho for fornecido e o schema `template_{nicho}` existir,
    ele será usado, copiando também os dados. Caso contrário,
    usa o `moura_schema` (somente estrutura).

    Args:
        schema_nome: Nome do novo schema (deve ser validado).
        tabelas: Lista de nomes de tabelas a serem replicadas.
        nicho: Área de atuação para buscar o template específico.
    """
    schema = validar_schema(schema_nome)
    
    try:
        with engine.begin() as conn:
            # 1. Determina o schema base
            schema_base = "moura_schema"
            usar_dados = False
            
            if nicho:
                # Sanitizar nome do nicho para evitar SQL Injection (já que vamos interpolar)
                import re
                nicho_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nicho.lower())
                nome_template = f"template_{nicho_limpo}"
                
                # Verifica se o template existe no banco
                result = conn.execute(text(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema_name"
                ), {"schema_name": nome_template})
                
                if result.fetchone():
                    schema_base = nome_template
                    usar_dados = True  # Para templates específicos, copiamos os dados (ex: serviços)
                    logger.info("Usando template específico para nicho: %s", schema_base)
                else:
                    logger.info("Template %s não encontrado. Usando moura_schema", nome_template)
            
            # 2. Cria o novo schema
            logger.info("Criando schema %s", schema)
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            
            # 3. Copia as tabelas
            for tabela in tabelas:
                logger.info(
                    "Copiando tabela %s de %s para %s",
                    tabela,
                    schema_base,
                    schema,
                )
                conn.execute(
                    text(
                        f"CREATE TABLE {schema}.{tabela} (LIKE {schema_base}.{tabela} INCLUDING ALL)"
                    )
                )
                
                # Se for para usar os dados do template (ex: serviços pré-cadastrados)
                if usar_dados:
                    conn.execute(text(f"INSERT INTO {schema}.{tabela} SELECT * FROM {schema_base}.{tabela}"))
                else:
                    conn.execute(text(f"TRUNCATE {schema}.{tabela}"))
                    
        logger.info("Schema %s criado com sucesso baseado em %s", schema, schema_base)
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
