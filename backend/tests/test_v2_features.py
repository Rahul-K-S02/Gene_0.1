import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_registration_and_login():
    email = f"test_user_{pytest.importorskip('time').time()}@example.com"
    reg_payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Test Patient"
    }
    
    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "token" in reg_data
    assert reg_data["email"] == email

    # 2. Login
    login_payload = {
        "email": email,
        "password": "Password123!"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "token" in login_data

def test_govt_schemes_endpoint_trilingual():
    # English
    res_en = client.get("/api/v1/govt-schemes?lang=en")
    assert res_en.status_code == 200
    schemes_en = res_en.json()
    assert len(schemes_en) >= 3
    assert any("Ayushman Bharat" in s["name"] for s in schemes_en)

    # Hindi
    res_hi = client.get("/api/v1/govt-schemes?lang=hi")
    assert res_hi.status_code == 200
    schemes_hi = res_hi.json()
    assert len(schemes_hi) >= 3
    assert any("आयुष्मान" in s["name"] for s in schemes_hi)

    # Kannada
    res_kn = client.get("/api/v1/govt-schemes?lang=kn")
    assert res_kn.status_code == 200
    schemes_kn = res_kn.json()
    assert len(schemes_kn) >= 3
    assert any("ಆಯುಷ್ಮಾನ್" in s["name"] for s in schemes_kn)

def test_medical_ai_agent_chat_intents():
    # Emergency
    res_emerg = client.post("/api/v1/agent-chat", json={
        "message": "I have severe chest pain and breathlessness",
        "language": "en"
    })
    assert res_emerg.status_code == 200
    data_emerg = res_emerg.json()
    assert data_emerg["intent_detected"] == "emergency_hospital"
    assert "108" in data_emerg["reply"] or "Emergency" in data_emerg["reply"]

    # Home remedy
    res_remedy = client.post("/api/v1/agent-chat", json={
        "message": "What is a safe home remedy for mild acidity?",
        "language": "en"
    })
    assert res_remedy.status_code == 200
    data_remedy = res_remedy.json()
    assert data_remedy["intent_detected"] == "home_remedy"
    assert len(data_remedy["suggested_actions"]) > 0

    # Govt scheme
    res_scheme = client.post("/api/v1/agent-chat", json={
        "message": "How do I get Ayushman Bharat 5 lakh free card?",
        "language": "en"
    })
    assert res_scheme.status_code == 200
    data_scheme = res_scheme.json()
    assert data_scheme["intent_detected"] == "govt_scheme"
    assert "PM-JAY" in data_scheme["reply"] or "Ayushman" in data_scheme["reply"]
