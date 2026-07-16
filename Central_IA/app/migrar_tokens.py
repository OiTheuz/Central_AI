import sys
import os

# Ajusta o path para importar 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Merchant
from app.config import META_ACCESS_TOKEN, META_PHONE_ID

def main():
    db = SessionLocal()
    try:
        jessiely = db.query(Merchant).filter(Merchant.nome_do_schema == 'jessiely_moura', Merchant.loja_pai_id == None).first()
        if jessiely:
            jessiely.meta_access_token = META_ACCESS_TOKEN
            jessiely.meta_phone_id = META_PHONE_ID
            db.commit()
            print('✅ Tokens da Jessiely Moura migrados do .env para o Banco de Dados com sucesso!')
        else:
            print('⚠️ Loja Jessiely Moura não encontrada no Banco.')
    except Exception as e:
        print(f"Erro ao migrar: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    main()
