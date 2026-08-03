import logging
from typing import List
from app.utils.niche_templates import get_services_for_niche

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
                logger.info("Usando map em código para nicho: %s. Banco base: moura_schema", nicho)
            
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
            
            # 3.5 Cria tabelas de profissionais explicitamente (já que não estão no moura_schema)
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema}.professionals (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {schema}.professional_shifts (
                    id SERIAL PRIMARY KEY,
                    professional_id INTEGER NOT NULL REFERENCES {schema}.professionals(id) ON DELETE CASCADE,
                    dia_semana INTEGER NOT NULL,
                    turno_inicio VARCHAR(5),
                    turno_fim VARCHAR(5),
                    dia_fechado BOOLEAN NOT NULL DEFAULT FALSE
                )
            """))
            
            # 4. Insere os serviços mapeados para o nicho (se houver)
            if nicho:
                servicos = get_services_for_niche(nicho)
                for svc in servicos:
                    conn.execute(text(
                        f"""
                        INSERT INTO {schema}.services 
                        (nome, preco, duracao_minutos, lembrete_ativo, lembrete_valor_intervalo, lembrete_tipo_intervalo) 
                        VALUES (:nome, :preco, :duracao, :lembrete_ativo, :lembrete_valor, :lembrete_tipo)
                        """
                    ), {
                        "nome": svc["nome"],
                        "preco": svc["preco"],
                        "duracao": svc["duracao_minutos"],
                        "lembrete_ativo": svc["lembrete_ativo"],
                        "lembrete_valor": svc["lembrete_valor"],
                        "lembrete_tipo": svc["lembrete_tipo"]
                    })
                    
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
