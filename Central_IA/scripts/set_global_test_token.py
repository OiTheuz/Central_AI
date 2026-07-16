import os
from sqlalchemy import create_engine, text

# Conecta ao banco de dados usando a variavel de ambiente ou localhost (se estiver rodando na VPS via script local da VPS)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:134001@localhost:5432/central_agendamento_db")
engine = create_engine(DATABASE_URL)

def update_env_token():
    with engine.begin() as conn:
        # Busca o token que esta funcionando no Petshop (o token de testes)
        result = conn.execute(text("SELECT meta_access_token FROM merchant WHERE area_atuacao = 'petshop' OR nome_do_schema LIKE '%pet%'")).fetchall()
        
        token = None
        for row in result:
            if row[0]:
                token = row[0]
                break
                
        if not token:
            print("❌ Token de teste não encontrado no Petshop.")
            return

        env_path = "/var/www/central_ai/.env"
        
        if not os.path.exists(env_path):
            print(f"❌ Arquivo {env_path} não encontrado.")
            return

        with open(env_path, "r") as f:
            lines = f.readlines()
            
        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith("META_ACCESS_TOKEN="):
                    f.write(f"META_ACCESS_TOKEN={token}\n")
                else:
                    f.write(line)
                    
        print("✅ Token de testes configurado como o Token Global no .env da VPS!")
        print("Agora qualquer nova loja de demonstração usará esse token automaticamente.")

if __name__ == "__main__":
    update_env_token()
