import pytest
from scripts.import_real_datasets import clump_and_threshold

def test_p_thresholding():
    """Verifies that variants with p >= 5e-8 are dropped."""
    associations = [
        {"rsid": "rs1", "chromosome": "1", "position": 1000, "disease_id": "cad", "p_value": 1e-10},
        {"rsid": "rs2", "chromosome": "1", "position": 50000, "disease_id": "cad", "p_value": 1e-4}, # Above threshold
    ]
    clumped = clump_and_threshold(associations, p_threshold=5e-8, window_bp=250_000)
    assert len(clumped) == 1
    assert clumped[0]["rsid"] == "rs1"

def test_distance_based_clumping_window():
    """Verifies that nearby SNPs within 250kb are collapsed to the lead SNP with lowest p-value."""
    associations = [
        # Lead SNP
        {"rsid": "rs_lead", "chromosome": "9", "position": 22100000, "disease_id": "cad", "p_value": 1e-40},
        # Nearby weaker SNP (20kb away)
        {"rsid": "rs_near", "chromosome": "9", "position": 22120000, "disease_id": "cad", "p_value": 1e-25},
        # Distant independent SNP (>300kb away)
        {"rsid": "rs_dist", "chromosome": "9", "position": 22500000, "disease_id": "cad", "p_value": 1e-30},
    ]
    
    clumped = clump_and_threshold(associations, p_threshold=5e-8, window_bp=250_000)
    
    retained_ids = [s["rsid"] for s in clumped]
    assert "rs_lead" in retained_ids
    assert "rs_dist" in retained_ids
    assert "rs_near" not in retained_ids
    assert len(clumped) == 2

def test_different_chromosomes_are_independent():
    """Verifies that variants on different chromosomes are not clumped against each other."""
    associations = [
        {"rsid": "rs_chr1", "chromosome": "1", "position": 1000000, "disease_id": "cad", "p_value": 1e-20},
        {"rsid": "rs_chr2", "chromosome": "2", "position": 1000000, "disease_id": "cad", "p_value": 1e-18},
    ]
    clumped = clump_and_threshold(associations, p_threshold=5e-8, window_bp=250_000)
    assert len(clumped) == 2
