import sys
import os

# Ajusta o path para importar 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Merchant

def main():
    db = SessionLocal()
    try:
        jessiely = db.query(Merchant).filter(Merchant.nome_do_schema == 'jessiely_moura', Merchant.loja_pai_id == None).first()
        if jessiely:
            jessiely.meta_access_token = "EAAYTjZC5uRkUBRZBUvNpHZAsWqQZBY7irAZCH2B3AZAChR4R4ZBOZBaUZCclcburGl1kvHmf7tZBj9CgIh1ZBgU7JNrlo5kctJZBiEEgEhvh9ZBNhKDowMRX1oC4VywWOQ7XvOAEXRAjZBRbyCLArKyLimuFLFcSr9ZAEF7OubfSqQBO9E5lwkFbL4UOy2w1dxg7afeO8IfdwZDZD"
            jessiely.meta_phone_id = "1238251112701602"
            db.commit()
            print('✅ Tokens da Jessiely Moura CORRIGIDOS no Banco de Dados com sucesso!')
        else:
            print('⚠️ Loja Jessiely Moura não encontrada no Banco.')
    except Exception as e:
        print(f"Erro ao corrigir: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    main()
