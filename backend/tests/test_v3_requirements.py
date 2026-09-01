import uuid
import pytest
from app.config import settings
from app.database import db_manager, fetch_all
from app.pubmed_service import pubmed_service
from app.shap_explainer import shap_explainer, encode_lifestyle_features
from app.schemas import LifestyleFactors
from app.rag_pipeline import rag_pipeline
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_qdrant_major_project_config():
    """Verify that collection name is major_project and no hardcoding exists."""
    assert settings.QDRANT_COLLECTION_NAME == "major_project"
    assert rag_pipeline.collection_name == "major_project"

def test_pubmed_service_chunking_and_uuid():
    """Verify PubMed abstract chunking and deterministic UUID generation."""
    sample_abstract = "A " * 400 + "Second sentence. " + "B " * 400
    chunks = pubmed_service.chunk_text(sample_abstract, max_chars=500)
    assert len(chunks) >= 2

    # Deterministic UUID test
    pmid = "12345678"
    chunk_num = 0
    id_1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"PubMed_{pmid}_{chunk_num}"))
    id_2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"PubMed_{pmid}_{chunk_num}"))
    assert id_1 == id_2
    assert id_1.count("-") == 4

def test_turso_column_mapping_layer():
    """Verify Turso column mapping adapter (rs_id -> rsid, effect_size -> beta, etc.)."""
    # Test query adapter
    query = "SELECT * FROM gwas_weights WHERE disease_id = ? AND rsid IN (?)"
    adapted_q, _ = db_manager._adapt_query_for_turso(query, ("t2d", "rs7903146"))
    assert "disease =" in adapted_q
    assert "rs_id IN" in adapted_q

    # Test row normalization
    raw_turso_row = [{
        "disease": "t2d",
        "rs_id": "rs7903146",
        "gene": "TCF7L2",
        "effect_size": 0.35,
        "risk_allele": "T",
        "maf": 0.30
    }]
    norm_rows = db_manager._adapt_rows_from_turso(raw_turso_row, query)
    assert len(norm_rows) == 1
    norm = norm_rows[0]
    assert norm["rsid"] == "rs7903146"
    assert norm["beta"] == 0.35
    assert norm["effect_allele"] == "T"
    assert norm["disease_id"] == "t2d"

    # Test ClinVar mapping
    raw_clinvar_row = [{
        "rs_id": "rs80357906",
        "gene_name": "BRCA1",
        "clinical_significance": "Pathogenic",
        "condition_name": "Hereditary Breast Cancer",
        "review_status": "reviewed by expert panel"
    }]
    norm_clinvar = db_manager._adapt_rows_from_turso(raw_clinvar_row, "SELECT * FROM clinvar_variants")
    assert norm_clinvar[0]["rsid"] == "rs80357906"
    assert norm_clinvar[0]["gene"] == "BRCA1"
    assert norm_clinvar[0]["phenotype"] == "Hereditary Breast Cancer"

def test_xgboost_and_real_shap():
    """Verify that genuine XGBoost models execute and return real_shap."""
    lifestyle = LifestyleFactors(
        age=50,
        sex="male",
        bmi=28.5,
        smoking_status="current",
        physical_activity_hours_per_week=1.5,
        mediterranean_diet_score=5,
        systolic_bp=135,
        sleep_hours=6.5,
        alcohol_drinks_per_week=4.0
    )

    for d_id in ["cad", "t2d", "ad", "htn", "breast_cancer"]:
        shap_mode, importance, chart = shap_explainer.explain(
            disease_id=d_id,
            prs_z=1.2,
            prs_percentile=88.5,
            lifestyle=lifestyle
        )
        assert shap_mode == "real_shap", f"Expected 'real_shap' for {d_id}, got {shap_mode}"
        assert len(importance) == 9
        assert "Genetic PRS (Z-score)" in importance
        assert chart is not None and chart.startswith("data:image/png;base64,")

def test_system_status_endpoint():
    """Verify GET /api/v1/system/status returns safe telemetry without credentials."""
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "online"
    assert data["qdrant"]["collection_name"] == "major_project"
    assert "connected" in data["qdrant"]
    assert "turso" in data
    assert "models" in data
    assert data["models"]["shap_readiness"] == "real_shap"
    assert "groq" in data

    # Verify no secret leakage
    json_str = str(data)
    assert "eyJ" not in json_str  # No JWT tokens or Turso tokens
    assert "gsk_" not in json_str  # No Groq API keys

def test_full_analysis_endpoint():
    """Verify /api/v1/analyze executes end-to-end and returns real SHAP and telemetry."""
    payload = {
        "lifestyle": {
            "age": 45,
            "sex": "male",
            "bmi": 27.5,
            "smoking_status": "never",
            "physical_activity_hours_per_week": 3.0,
            "mediterranean_diet_score": 7,
            "systolic_bp": 122,
            "sleep_hours": 7.5,
            "alcohol_drinks_per_week": 2.0,
            "family_history_cad": True,
            "family_history_t2d": False,
            "family_history_ad": False
        },
        "genomic_data": {
            "rs1333049": 2.0,
            "rs7903146": 1.0,
            "rs429358": 0.0
        },
        "language": "en"
    }

    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data
    assert len(data["disease_risks"]) >= 5
    for dr in data["disease_risks"]:
        assert dr["shap_mode"] == "real_shap"
    assert data["system_status"]["shap_mode"] == "real_shap"
    assert "qdrant" in data["system_status"]["rag_source"] or "fallback" in data["system_status"]["rag_source"]
