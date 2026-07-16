import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, engine
from app.services.auth_service import hash_senha
from app.services.schema_service import criar_novo_estabelecimento
from sqlalchemy import text

def criar_petshop():
    db = SessionLocal()
    
    email = "petshop@teste.com"
    
    # 1. Verifica se já existe
    result = db.execute(text("SELECT id FROM merchant WHERE email = :email"), {"email": email}).fetchone()
    
    if result:
        print("A loja Pet Shop já existe no banco de dados!")
    else:
        # Pega a senha criptografada
        senha = hash_senha("123")
        
        # Insere a nova loja via SQL puro para evitar erros se o seu banco local estiver desatualizado
        db.execute(text("""
            INSERT INTO merchant (nome_loja, codigo_loja, nome_do_schema, email, senha_hash, area_atuacao)
            VALUES ('Meu Pet Shop Modelo', 'pet01', 'petshop_demo', :email, :senha, 'petshop')
        """), {"email": email, "senha": senha})
        
        db.commit()
        print("Usuario do Pet Shop criado com sucesso na tabela merchant!")

    # 2. Cria as tabelas do Pet Shop no schema dele
    print("Criando o banco de dados (schema) do Pet Shop...")
    try:
        criar_novo_estabelecimento("petshop_demo", ["appointments", "customers", "services"], "petshop")
        print("Banco do Pet Shop criado e populado com os servicos de Banho e Tosa!")
    except Exception as e:
        print(f"Aviso ao criar schema: {e}")
        
    print("\n=============================================")
    print(" Tudo pronto! Faca login no aplicativo com:")
    print(f" Email: {email}")
    print(" Senha: 123")
    print("=============================================")

if __name__ == "__main__":
    criar_petshop()
