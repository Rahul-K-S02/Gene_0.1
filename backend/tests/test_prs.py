import math
import pytest
from scipy.stats import norm

from app.prs_engine import PRSEngine
from app.database import init_tables, execute_script, execute_query

@pytest.fixture(autouse=True)
def setup_test_db():
    init_tables()
    # Insert test SNP panel
    execute_query(
        """
        INSERT OR REPLACE INTO gwas_weights 
        (rsid, chromosome, position, gene, disease_id, disease_name, effect_allele, other_allele, beta, maf, p_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("rs1333049", "9", 22125503, "CDKN2A/B", "test_cad", "Test CAD", "C", "G", 0.40, 0.50, 1e-20)
    )
    execute_query(
        """
        INSERT OR REPLACE INTO gwas_weights 
        (rsid, chromosome, position, gene, disease_id, disease_name, effect_allele, other_allele, beta, maf, p_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("rs693", "2", 21237554, "APOB", "test_cad", "Test CAD", "T", "C", 0.20, 0.30, 1e-15)
    )

def test_prs_standardization_math():
    """Verifies that an average individual (dosage = 2*MAF) yields Z-score of 0 and 50th percentile."""
    engine = PRSEngine()
    
    # Average individual: dosage equal to 2*MAF
    # rs1333049 (MAF 0.50 -> dosage 1.0)
    # rs693 (MAF 0.30 -> dosage 0.60)
    user_dosages = {
        "rs1333049": 1.0,
        "rs693": 0.60
    }
    
    result = engine.compute_disease_prs("test_cad", user_dosages)
    
    assert abs(result["standardized_z"]) < 1e-2, f"Expected Z ~ 0, got {result['standardized_z']}"
    assert 48.0 <= result["percentile"] <= 52.0, f"Expected percentile ~ 50%, got {result['percentile']}"
    assert result["snps_found"] == 2
    assert result["confidence_score"] == 1.0

def test_high_risk_prs_percentile():
    """Verifies that homozygous risk alleles (dosage=2.0) yield high positive Z-score and percentile > 85%."""
    engine = PRSEngine()
    
    user_dosages = {
        "rs1333049": 2.0,
        "rs693": 2.0
    }
    
    result = engine.compute_disease_prs("test_cad", user_dosages)
    
    assert result["standardized_z"] > 1.0, f"Expected Z > 1.0, got {result['standardized_z']}"
    assert result["percentile"] > 85.0, f"Expected percentile > 85%, got {result['percentile']}"

def test_missing_snp_neutral_imputation():
    """Verifies that missing SNPs are neutrally imputed to population expectation without crashing."""
    engine = PRSEngine()
    
    # Only supply 1 of 2 SNPs
    user_dosages = {
        "rs1333049": 1.0
    }
    
    result = engine.compute_disease_prs("test_cad", user_dosages)
    
    assert result["snps_found"] == 1
    assert result["snps_total"] == 2
    assert result["confidence_score"] == 0.5
    assert 45.0 <= result["percentile"] <= 55.0
