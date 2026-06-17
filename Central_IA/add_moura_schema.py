from sqlalchemy import text
from app.database import engine

def add_moura():
    with engine.connect() as conn:
        # Verifica se já existe
        existe = conn.execute(
            text("SELECT id FROM merchant WHERE nome_do_schema = 'moura_schema'")
        ).fetchone()

        if existe:
            print("❌ 'moura_schema' já está na tabela merchant.")
            return

        # Insere na tabela
        conn.execute(
            text("""
                INSERT INTO merchant (
                    nome_loja, codigo_loja, nome_do_schema, area_atuacao,
                    is_admin, tem_dashboard, pode_editar_servicos
                ) VALUES (
                    'Loja Moura', 'MOURA', 'moura_schema', 'Beleza',
                    false, true, true
                )
            """)
        )
        conn.commit()
        print("✅ 'moura_schema' inserido com sucesso na tabela merchant!")

if __name__ == "__main__":
    add_moura()
