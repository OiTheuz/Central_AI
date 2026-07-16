import os
from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()
db.execute(text("UPDATE merchant SET email = 'admin' WHERE email = 'admin@lautz.tech'"))
db.commit()
print('DB UPDATED VPS')
