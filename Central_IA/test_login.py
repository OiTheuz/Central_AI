import requests

try:
    res = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"email": "moura@teste.com", "senha": "123"}
    )
    print("STATUS:", res.status_code)
    print("RESPOSTA:", res.text)
except Exception as e:
    print("ERRO:", e)
