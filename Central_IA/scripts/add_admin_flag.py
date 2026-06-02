import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Adiciona a coluna is_admin se não existir
db.execute(text("""
    ALTER TABLE merchant 
    ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE
"""))
db.commit()

# Marca seu usuário como admin
db.execute(text("""
    UPDATE merchant SET is_admin = TRUE WHERE email = 'moura@teste.com'
"""))
db.commit()

db.close()
print("Coluna is_admin criada e seu usuário marcado como admin!")
