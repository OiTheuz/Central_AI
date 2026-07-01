import os
import sys

# Garante que consiga importar os módulos do app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def compare_schemas(schema_origem="jessiely_moura", schema_destino="moura_schema"):
    print(f"Comparando o schema '{schema_destino}' para ver se falta algo em relação ao '{schema_origem}'...")
    
    comandos_sql = []
    
    with engine.connect() as conn:
        # Pega todas as tabelas
        tabelas_origem = conn.execute(text(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{schema_origem}' AND table_type = 'BASE TABLE'
        """)).fetchall()
        
        tabelas_destino = conn.execute(text(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{schema_destino}' AND table_type = 'BASE TABLE'
        """)).fetchall()
        
        set_tab_origem = {t[0] for t in tabelas_origem}
        set_tab_destino = {t[0] for t in tabelas_destino}
        
        # Tabelas que faltam
        tabelas_faltando = set_tab_origem - set_tab_destino
        for tab in tabelas_faltando:
            comandos_sql.append(f"CREATE TABLE {schema_destino}.{tab} (LIKE {schema_origem}.{tab} INCLUDING ALL);")
            
        # Pega todas as colunas
        colunas_origem = conn.execute(text(f"""
            SELECT table_name, column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_schema = '{schema_origem}'
        """)).fetchall()
        
        colunas_destino = conn.execute(text(f"""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema = '{schema_destino}'
        """)).fetchall()
        
        set_col_destino = {(c[0], c[1]) for c in colunas_destino}
        
        # Colunas que faltam nas tabelas que JÁ EXISTEM
        for r in colunas_origem:
            tabela, coluna, tipo, length = r[0], r[1], r[2], r[3]
            # Ignora colunas de tabelas que já vamos recriar do zero
            if tabela in tabelas_faltando:
                continue
                
            if (tabela, coluna) not in set_col_destino:
                tipo_sql = tipo
                if tipo == 'character varying' and length:
                    tipo_sql = f"VARCHAR({length})"
                comandos_sql.append(f"ALTER TABLE {schema_destino}.{tabela} ADD COLUMN IF NOT EXISTS {coluna} {tipo_sql} NULL;")
                
    if not comandos_sql:
        print(f"\\nO schema '{schema_destino}' já está 100% IGUAL ao '{schema_origem}'!")
    else:
        print("\\n=== ENCONTRAMOS DIFERENÇAS! Rode estes comandos no banco de dados para igualar: ===\\n")
        print("sudo -u postgres psql -d central_agendamento_db -c \\"")
        for cmd in comandos_sql:
            print(f"  {cmd}")
        print("\\"")
        print("\\n==================================================================================")

if __name__ == "__main__":
    compare_schemas()
