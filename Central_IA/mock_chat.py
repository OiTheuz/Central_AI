import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.chat import ClientChatState, ChatMessage
from app.models import Merchant

def main():
    db = SessionLocal()
    try:
        # Pega o primeiro lojista (ou ajuste se quiser um específico)
        lojista = db.query(Merchant).first()
        if not lojista:
            print("Nenhum lojista encontrado!")
            return
            
        print(f"Usando lojista: {lojista.nome_do_schema}")
            
        # Pega um estado de chat existente ou cria um novo
        chat_state = db.query(ClientChatState).filter(
            ClientChatState.merchant_id == lojista.id
        ).first()
        
        if not chat_state:
            chat_state = ClientChatState(
                merchant_id=lojista.id,
                client_phone="5511999999999",
                client_name="Cliente de Teste"
            )
            db.add(chat_state)
            
        # Marca como aguardando atendimento humano
        chat_state.is_human_service = True
        chat_state.human_service_started_at = datetime.now(timezone.utc)
        
        # Adiciona uma mensagem fake só pra ter algo lá
        msg = ChatMessage(
            merchant_id=lojista.id,
            client_phone=chat_state.client_phone,
            message_content="Quero falar com um humano, por favor!",
            sender="client",
            read=False
        )
        db.add(msg)
        
        db.commit()
        print(f"✅ Chat pendente criado/atualizado para o telefone: {chat_state.client_phone}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
