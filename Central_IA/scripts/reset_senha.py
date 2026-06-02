import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.services.auth_service import hash_senha
from app.database import SessionLocal
from sqlalchemy import text

# ─── Configuração ───────────────────────────────────────
EMAIL = "moura@teste.com"     # Email do merchant
NOVA_SENHA = "123"            # Nova senha desejada
# ────────────────────────────────────────────────────────

db = SessionLocal()
novo_hash = hash_senha(NOVA_SENHA)
db.execute(
    text("UPDATE merchant SET senha_hash = :h WHERE email = :e"),
    {"h": novo_hash, "e": EMAIL}
)
db.commit()
db.close()
print(f"Senha atualizada para {EMAIL}!")
