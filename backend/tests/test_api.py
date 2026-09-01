import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_tables

@pytest.fixture(autouse=True)
def setup_api_env():
    init_tables()

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "GeneRisk"

def test_supported_panel_endpoint():
    response = client.get("/api/v1/supported-panel")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_demo_samples_endpoint():
    response = client.get("/api/v1/demo-samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 4
    assert "sample_cad_high" in [s["id"] for s in samples]

def test_analyze_endpoint_json_payload():
    payload = {
        "lifestyle": {
            "age": 50,
            "sex": "male",
            "bmi": 28.0,
            "smoking_status": "former",
            "physical_activity_hours_per_week": 2.0,
            "mediterranean_diet_score": 6,
            "systolic_bp": 130,
            "sleep_hours": 7.0,
            "alcohol_drinks_per_week": 3.0,
            "family_history_cad": True,
            "family_history_t2d": False,
            "family_history_ad": False
        },
        "genomic_data": {
            "rs1333049": 2.0,
            "rs693": 1.0,
            "rs7903146": 1.0,
            "rs4149056": 1.0
        },
        "language": "en"
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "analysis_id" in data
    assert len(data["disease_risks"]) > 0
    assert "pdf_report_base64" in data
    assert data["pdf_report_base64"] is not None
    assert len(data["ai_lifestyle_prescriptions"]) >= 2

def test_simulate_endpoint():
    payload = {
        "disease_id": "cad",
        "base_prs_percentile": 85.0,
        "base_prs_z": 1.04,
        "lifestyle": {
            "age": 50,
            "sex": "male",
            "bmi": 32.0,
            "smoking_status": "current",
            "physical_activity_hours_per_week": 0.0,
            "mediterranean_diet_score": 3,
            "systolic_bp": 150,
            "sleep_hours": 5.5,
            "alcohol_drinks_per_week": 10.0,
            "family_history_cad": True,
            "family_history_t2d": False,
            "family_history_ad": False
        }
    }
    
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "simulated_relative_risk" in data
    assert "simulated_absolute_risk_10yr" in data
    assert len(data["actionable_levers"]) > 0

def test_chat_endpoint():
    payload = {
        "question": "What does my 9p21.3 result mean?",
        "report_summary": {"highest_risk": "Coronary Artery Disease", "percentile": 88.0},
        "language": "en"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 20
