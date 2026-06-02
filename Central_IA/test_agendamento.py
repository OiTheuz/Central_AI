from app.database import SessionLocal, text
from sqlalchemy.orm import Session
import traceback

def test_insert():
    db = SessionLocal()
    try:
        # Set schema
        db.execute(text("SET search_path TO moura_schema, public"))
        
        # Test insert customer
        db.execute(
            text("""
                INSERT INTO customers (nome, telefone_whatsapp)
                VALUES (:nome, :tel)
                ON CONFLICT (telefone_whatsapp) DO UPDATE SET nome = EXCLUDED.nome
            """),
            {"nome": "Teste", "tel": "11999999999"}
        )
        db.commit()
        
        cliente = db.execute(
            text("SELECT id FROM customers WHERE telefone_whatsapp = :tel"),
            {"tel": "11999999999"}
        ).mappings().fetchone()
        print("Cliente ID:", cliente["id"])

        # Insert appointment
        db.execute(
            text("""
                INSERT INTO appointments (customer_id, service_id, data_agendamento, horario_agendamento, status)
                VALUES (:c_id, :s_id, :data, :hora, 'aprovado')
            """),
            {
                "c_id": cliente["id"],
                "s_id": 1,
                "data": "2026-05-30",
                "hora": "14:00",
            }
        )
        db.commit()
        print("Sucesso!")

    except Exception as e:
        print("Erro:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_insert()
