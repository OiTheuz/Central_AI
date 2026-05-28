import requests

try:
    res = requests.post(
        "http://localhost:8000/api/auth/set-password",
        json={"codigo_loja": "MOURA01", "email": "moura@teste.com", "senha": "123"}
    )
    print(res.status_code)
    print(res.text)
except Exception as e:
    print(e)
