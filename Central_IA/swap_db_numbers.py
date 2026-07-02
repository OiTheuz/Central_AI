import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
with engine.begin() as conn:
    conn.execute(text("UPDATE public.merchant SET numero_whatsapp = 'TEMP1' WHERE LOWER(nome_do_schema) = 'jessiely_moura';"))
    conn.execute(text("UPDATE public.merchant SET numero_whatsapp = 'TEMP2' WHERE nome_do_schema = 'moura_schema';"))
    
    conn.execute(text("UPDATE public.merchant SET numero_whatsapp = '1235152459670673' WHERE LOWER(nome_do_schema) = 'jessiely_moura';"))
    conn.execute(text("UPDATE public.merchant SET numero_whatsapp = '554188894240' WHERE nome_do_schema = 'moura_schema';"))
    
    print("Local DB atualizado!")
