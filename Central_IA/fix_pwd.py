# coding: utf-8
with open("app/routers/app_lojista.py", "a", encoding="utf-8") as f:
    f.write('''

class ChangePasswordRequestMobile(BaseModel):
    nova_senha: str

@router.post("/auth/change-password")
def change_password_mobile(
    body: ChangePasswordRequestMobile,
    merchant: Merchant = Depends(get_lojista_atual)
):
    """Permite ao usuário logado alterar sua própria senha pelo app mobile."""
    from app.services.auth_service import hash_senha
    from app.database import SessionLocal
    
    with SessionLocal() as public_db:
        pub_merchant = public_db.query(Merchant).filter(Merchant.id == merchant.id).first()
        if pub_merchant:
            pub_merchant.senha_hash = hash_senha(body.nova_senha)
            public_db.commit()
            
    return {"status": "sucesso", "mensagem": "Senha alterada com sucesso!"}
''')
print("Rota de senha adicionada no app_lojista.py!")
