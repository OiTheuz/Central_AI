import requests
import time

url = "http://localhost:8000/webhook"
payload = {
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "id": f"test_msg_{int(time.time())}",
                "from": "5511999999999",
                "type": "text",
                "timestamp": str(int(time.time())),
                "text": {
                  "body": "Quero agendar um corte na Barbearia Moura"
                }
              }
            ]
          }
        }
      ]
    }
  ]
}

res = requests.post(url, json=payload)
print("Status Code:", res.status_code)
print("Response:", res.text)
