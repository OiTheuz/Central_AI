from app.database import SessionLocal
from app.routers.auth import login, LoginRequest

db = SessionLocal()
try:
    req = LoginRequest(email="moura@teste.com", senha="123")
    res = login(req, db)
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
