from app.database import SessionLocal
from app.routers.auth import set_password, SetPasswordRequest

db = SessionLocal()
try:
    req = SetPasswordRequest(codigo_loja="MOURA01", email="moura@teste.com", senha="123")
    res = set_password(req, db)
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
