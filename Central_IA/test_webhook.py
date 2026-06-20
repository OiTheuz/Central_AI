import requests
import json

url = "http://187.77.42.116:8000/api/webhook"
payload = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "123456",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "5511999999999",
                            "phone_number_id": "5511999999999"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "Matheus"
                                },
                                "wa_id": "5511999998888"
                            }
                        ],
                        "messages": [
                            {
                                "from": "5511999998888",
                                "id": "wamid.123",
                                "timestamp": "1620000000",
                                "text": {
                                    "body": "Oi"
                                },
                                "type": "text"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)
