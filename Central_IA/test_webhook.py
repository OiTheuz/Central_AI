import asyncio
from app.routers.webhook import processar_mensagem
from app.database import engine
from sqlalchemy.orm import Session

async def test_webhook():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "123", "phone_number_id": "123"},
                            "contacts": [{"profile": {"name": "Test User"}, "wa_id": "554187450272"}],
                            "messages": [
                                {
                                    "from": "554187450272",
                                    "id": "wamid.XYZ123",
                                    "timestamp": "1234567890",
                                    "type": "text",
                                    "text": {"body": "Oi"}
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    with Session(engine) as db:
        try:
            await processar_mensagem(payload, db)
            print("Sucesso!")
        except Exception as e:
            print("ERRO:", repr(e))

if __name__ == "__main__":
    asyncio.run(test_webhook())
