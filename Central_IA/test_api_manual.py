import requests

def test_full_api():
    base_url = "http://127.0.0.1:8000"
    
    # Login as merchant to get token
    login_res = requests.post(f"{base_url}/api/mobile/login", json={
        "email": "moura@teste.com",
        "senha": "123"
    })
    
    if login_res.status_code != 200:
        print("Login failed:", login_res.text)
        return
        
    token = login_res.json()["token"]
    print("Token obtido:", token)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Try agendamento manual
    data = {
        "clienteNome": "Teste Manual",
        "clienteTelefone": "11999999999",
        "servicoId": 1,
        "data": "2026-05-30",
        "hora": "14:00"
    }
    
    res = requests.post(f"{base_url}/api/mobile/agendamentos/manual", headers=headers, json=data)
    print("Status code:", res.status_code)
    print("Response text:", res.text)

if __name__ == "__main__":
    test_full_api()
