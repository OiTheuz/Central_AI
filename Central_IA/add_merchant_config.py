"""
Script de migração: adiciona colunas de configuração de agendamento
na tabela merchant (schema public).

Execute: .venv\\Scripts\\python.exe add_merchant_config.py
"""
from app.database import engine
from sqlalchemy import text


def migrate():
    with engine.connect() as conn:
        cols = [
            ("permitir_sobreposicao", "BOOLEAN NOT NULL DEFAULT false"),
            ("horario_abertura",     "VARCHAR(5) NOT NULL DEFAULT '08:00'"),
            ("horario_fechamento",   "VARCHAR(5) NOT NULL DEFAULT '18:00'"),
        ]
        for col_name, col_def in cols:
            try:
                conn.execute(text(
                    f"ALTER TABLE merchant ADD COLUMN {col_name} {col_def};"
                ))
                conn.commit()
                print(f"[OK] Coluna '{col_name}' adicionada.")
            except Exception as e:
                conn.rollback()
                print(f"[SKIP] Coluna '{col_name}' ja existe ou erro: {e}")


if __name__ == "__main__":
    migrate()
