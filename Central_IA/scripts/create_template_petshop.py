import os
import sys

# Adiciona o diretório raiz ao path para poder importar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.database import engine

def create_template_petshop():
    print("Iniciando a criação do template_petshop...")
    
    try:
        with engine.begin() as conn:
            # 1. Cria o schema
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS template_petshop"))
            print("Schema 'template_petshop' criado ou já existia.")
            
            # 2. Cria as tabelas copiando de moura_schema
            tabelas = ["appointments", "customers", "services"]
            for tabela in tabelas:
                # Remove se já existir para poder rodar o script novamente de forma idempotente
                conn.execute(text(f"DROP TABLE IF EXISTS template_petshop.{tabela} CASCADE"))
                
                print(f"Copiando estrutura da tabela {tabela}...")
                conn.execute(
                    text(f"CREATE TABLE template_petshop.{tabela} (LIKE moura_schema.{tabela} INCLUDING ALL)")
                )
            
            # 3. Insere serviços iniciais de Pet Shop
            print("Inserindo serviços padrão...")
            servicos = [
                {"nome": "Banho", "preco": 50.00, "duracao_minutos": 60},
                {"nome": "Tosa", "preco": 70.00, "duracao_minutos": 60},
                {"nome": "Banho e Tosa", "preco": 100.00, "duracao_minutos": 120},
                {"nome": "Hidratação", "preco": 40.00, "duracao_minutos": 30},
                {"nome": "Corte de Unhas", "preco": 20.00, "duracao_minutos": 15},
            ]
            
            for servico in servicos:
                conn.execute(
                    text("""
                        INSERT INTO template_petshop.services (nome, preco, duracao_minutos) 
                        VALUES (:nome, :preco, :duracao_minutos)
                    """),
                    servico
                )
                
            print("Sucesso! O template 'template_petshop' foi criado com serviços padrão.")
            
    except Exception as e:
        print(f"Erro ao criar template: {e}")

if __name__ == "__main__":
    create_template_petshop()
