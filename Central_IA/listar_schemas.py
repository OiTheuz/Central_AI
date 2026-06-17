from sqlalchemy import text
from app.database import engine

def listar():
    with engine.connect() as conn:
        # Busca todos os schemas ignorando os schemas do sistema
        schemas = conn.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            AND schema_name NOT LIKE 'pg_temp_%'
            AND schema_name NOT LIKE 'pg_toast_temp_%'
            ORDER BY schema_name
        """)).fetchall()

        print("=== SCHEMAS ENCONTRADOS NO BANCO ===")
        if not schemas:
            print("Nenhum schema encontrado.")
            return

        for (schema_name,) in schemas:
            # Conta quantas tabelas existem nesse schema
            tabelas = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = :schema
            """), {"schema": schema_name}).fetchall()
            
            print(f"\n📁 Schema: {schema_name} ({len(tabelas)} tabelas)")
            if tabelas:
                # Mostra o nome de algumas tabelas para contexto
                nomes_tabelas = [t[0] for t in tabelas]
                print(f"   Tabelas: {', '.join(nomes_tabelas)}")

if __name__ == "__main__":
    listar()
