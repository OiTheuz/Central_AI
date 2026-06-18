import sys
import os

# Adiciona o diretório principal do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from sqlalchemy import text

def run():
    print("Iniciando migração para adicionar bloqueios...")
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE merchant ADD COLUMN dias_fechados VARCHAR(50);"))
            print("Coluna 'dias_fechados' adicionada.")
        except Exception as e:
            print(f"Aviso ao adicionar dias_fechados: {e}")

        try:
            conn.execute(text("ALTER TABLE merchant ADD COLUMN horario_almoco_inicio VARCHAR(5);"))
            print("Coluna 'horario_almoco_inicio' adicionada.")
        except Exception as e:
            print(f"Aviso ao adicionar horario_almoco_inicio: {e}")

        try:
            conn.execute(text("ALTER TABLE merchant ADD COLUMN horario_almoco_fim VARCHAR(5);"))
            print("Coluna 'horario_almoco_fim' adicionada.")
        except Exception as e:
            print(f"Aviso ao adicionar horario_almoco_fim: {e}")

    print("Migração concluída!")

if __name__ == "__main__":
    run()
