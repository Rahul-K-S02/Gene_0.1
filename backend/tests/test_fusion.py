import pytest
from app.schemas import LifestyleFactors
from app.lifestyle_fusion import fuse_genetic_and_lifestyle_risk, compute_lifestyle_multipliers

def test_healthy_lifestyle_reduces_risk():
    """Verifies that an optimal lifestyle produces lifestyle_rr < 1.0."""
    healthy_lifestyle = LifestyleFactors(
        age=45,
        sex="male",
        bmi=22.5,
        smoking_status="never",
        physical_activity_hours_per_week=4.0,
        mediterranean_diet_score=9,
        systolic_bp=115,
        sleep_hours=7.5,
        alcohol_drinks_per_week=1.0
    )
    
    lifestyle_rr, mults, drivers = compute_lifestyle_multipliers(healthy_lifestyle, "cad")
    assert lifestyle_rr < 1.0, f"Expected protective RR < 1.0, got {lifestyle_rr}"
    assert mults["smoking"] <= 0.95
    assert mults["physical_activity"] <= 0.85

def test_high_risk_lifestyle_increases_risk():
    """Verifies that smoking, obesity, and hypertension sharply increase relative risk."""
    poor_lifestyle = LifestyleFactors(
        age=55,
        sex="male",
        bmi=34.0,
        smoking_status="current",
        physical_activity_hours_per_week=0.0,
        mediterranean_diet_score=3,
        systolic_bp=155,
        sleep_hours=5.0,
        alcohol_drinks_per_week=16.0
    )
    
    lifestyle_rr, mults, drivers = compute_lifestyle_multipliers(poor_lifestyle, "cad")
    assert lifestyle_rr > 1.5, f"Expected elevated RR > 1.5, got {lifestyle_rr}"
    assert len(drivers) >= 4

def test_late_fusion_bounding_and_attribution():
    """Verifies that fused absolute risk is bounded properly and attribution sums to 100%."""
    lifestyle = LifestyleFactors()
    fusion = fuse_genetic_and_lifestyle_risk(
        disease_id="cad",
        prs_standardized_z=1.5,
        prs_percentile=93.3,
        lifestyle=lifestyle
    )
    
    assert 0.01 <= fusion["fused_absolute_risk_10yr"] <= 0.95
    assert abs((fusion["genetic_contribution_pct"] + fusion["lifestyle_contribution_pct"]) - 100.0) < 0.5
    assert fusion["risk_category"] in ("Low", "Average", "Elevated", "High")
