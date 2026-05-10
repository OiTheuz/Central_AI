import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from sqlalchemy import text # Importante para mudar de schema


# Carrega as variáveis do arquivo .env
load_dotenv()

# Pega a URL do banco de dados que você colocou no .env
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Cria o "motor" de conexão com o banco
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria a fábrica de sessões (como se fossem "conversas" com o banco)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criar as nossas tabelas depois
Base = declarative_base()

def verificar_disponibilidade(schema_nome, data, hora, servico):
    # Criamos uma sessão com o banco
    db = SessionLocal()
    try:
        # 1. Mudamos o 'caminho' do banco para o schema do lojista específico
        db.execute(text(f"SET search_path TO {schema_nome}"))
        
        # 2. Procuramos na tabela de horários desse lojista
        # Vamos assumir que sua tabela se chama 'horarios_disponiveis'
        query = text("""
            SELECT id FROM horarios_disponiveis 
            WHERE data = :data AND hora = :hora AND servico = :servico AND disponivel = TRUE
        """)
        
        resultado = db.execute(query, {"data": data, "hora": hora, "servico": servico}).fetchone()
        
        return resultado is not None # Retorna True se achar o horário, False se não
    finally:
        db.close() 