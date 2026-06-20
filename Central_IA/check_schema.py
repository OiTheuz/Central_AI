import sqlite3
import os
from sqlalchemy import create_engine, inspect

# URL from config or hardcoded for test
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/central_ia"
engine = create_engine(DATABASE_URL)

inspector = inspect(engine)
columns = inspector.get_columns('appointments', schema='jessiely_moura')
for c in columns:
    print(c['name'], c['type'], c['nullable'], c.get('default'))
