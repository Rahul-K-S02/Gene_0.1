import math
import logging
from typing import Dict, Any, Tuple, List
from app.schemas import LifestyleFactors

logger = logging.getLogger("generisk.fusion")

# Published disease-specific baseline 10-year incidence rates (general population age 40-70)
BASELINE_10YR_RISK = {
    "cad": 0.085,          # 8.5% 10-yr coronary artery disease
    "t2d": 0.095,          # 9.5% 10-yr type 2 diabetes
    "ad": 0.035,           # 3.5% 10-yr Alzheimer's disease (age-adjusted)
    "htn": 0.180,          # 18.0% 10-yr hypertension
    "breast_cancer": 0.040 # 4.0% 10-yr breast cancer (female baseline)
}

# Genetic vs Lifestyle weighting per disease (based on twin/epidemiological heritability estimates)
HERITABILITY_WEIGHTS = {
    "cad": {"genetic": 0.45, "lifestyle": 0.55},
    "t2d": {"genetic": 0.40, "lifestyle": 0.60},
    "ad": {"genetic": 0.65, "lifestyle": 0.35},
    "htn": {"genetic": 0.35, "lifestyle": 0.65},
    "breast_cancer": {"genetic": 0.50, "lifestyle": 0.50}
}

def compute_lifestyle_multipliers(lifestyle: LifestyleFactors, disease_id: str) -> Tuple[float, Dict[str, float], List[str]]:
    """
    Computes disease-specific relative risk (RR) multipliers and identifies actionable risk drivers.
    Returns: (lifestyle_rr, individual_multipliers, risk_driver_descriptions)
    """
    drivers = []
    mults = {}

    # 1. BMI Effect
    if lifestyle.bmi < 18.5:
        bmi_rr = 1.05
    elif 18.5 <= lifestyle.bmi < 25.0:
        bmi_rr = 0.95
    elif 25.0 <= lifestyle.bmi < 30.0:
        bmi_rr = 1.15
        if disease_id in ("cad", "t2d", "htn"):
            drivers.append(f"Overweight BMI ({lifestyle.bmi:.1f} kg/m²)")
    elif 30.0 <= lifestyle.bmi < 35.0:
        bmi_rr = 1.45 if disease_id == "t2d" else 1.30
        drivers.append(f"Class I Obesity BMI ({lifestyle.bmi:.1f} kg/m²)")
    else:
        bmi_rr = 1.85 if disease_id == "t2d" else 1.55
        drivers.append(f"Class II+ Obesity BMI ({lifestyle.bmi:.1f} kg/m²)")
    mults["bmi"] = bmi_rr

    # 2. Smoking Status
    if lifestyle.smoking_status == "current":
        smk_rr = 2.10 if disease_id in ("cad", "htn") else 1.35
        drivers.append("Current cigarette smoking")
    elif lifestyle.smoking_status == "former":
        smk_rr = 1.20 if disease_id in ("cad", "htn") else 1.05
    else:
        smk_rr = 0.90
    mults["smoking"] = smk_rr

    # 3. Physical Activity
    act = lifestyle.physical_activity_hours_per_week
    if act >= 3.5:
        act_rr = 0.80
    elif act >= 1.5:
        act_rr = 0.92
    elif act > 0.0:
        act_rr = 1.12
        drivers.append(f"Low physical activity ({act:.1f} hrs/week)")
    else:
        act_rr = 1.30
        drivers.append("Sedentary lifestyle (0 hrs/week activity)")
    mults["physical_activity"] = act_rr

    # 4. Mediterranean Diet Score (0-10)
    diet = lifestyle.mediterranean_diet_score
    if diet >= 8:
        diet_rr = 0.85
    elif diet >= 5:
        diet_rr = 1.00
    else:
        diet_rr = 1.25
        drivers.append(f"Suboptimal diet quality (Score {diet}/10)")
    mults["diet"] = diet_rr

    # 5. Systolic Blood Pressure
    sbp = lifestyle.systolic_bp
    if sbp >= 140:
        sbp_rr = 1.60 if disease_id in ("cad", "htn") else 1.20
        drivers.append(f"Stage 2 Systolic Hypertension ({sbp} mmHg)")
    elif sbp >= 130:
        sbp_rr = 1.30 if disease_id in ("cad", "htn") else 1.10
        drivers.append(f"Stage 1 Elevated SBP ({sbp} mmHg)")
    elif sbp < 110:
        sbp_rr = 0.95
    else:
        sbp_rr = 1.00
    mults["blood_pressure"] = sbp_rr

    # 6. Sleep Duration
    sleep = lifestyle.sleep_hours
    if 7.0 <= sleep <= 8.5:
        sleep_rr = 0.95
    elif sleep < 6.0:
        sleep_rr = 1.20 if disease_id in ("cad", "t2d", "ad") else 1.10
        drivers.append(f"Chronic sleep restriction ({sleep:.1f} hrs/night)")
    elif sleep > 9.5:
        sleep_rr = 1.15
    else:
        sleep_rr = 1.02
    mults["sleep"] = sleep_rr

    # 7. Alcohol Intake
    alc = lifestyle.alcohol_drinks_per_week
    if alc > 14:
        alc_rr = 1.35 if disease_id in ("htn", "breast_cancer") else 1.15
        drivers.append(f"High alcohol intake ({alc:.0f} drinks/week)")
    elif alc > 7:
        alc_rr = 1.15 if disease_id in ("htn", "breast_cancer") else 1.05
    else:
        alc_rr = 0.98
    mults["alcohol"] = alc_rr

    # 8. Family History Modifier
    fam_mod = 1.0
    if disease_id == "cad" and lifestyle.family_history_cad:
        fam_mod = 1.35
        drivers.append("First-degree family history of premature CAD")
    elif disease_id == "t2d" and lifestyle.family_history_t2d:
        fam_mod = 1.40
        drivers.append("First-degree family history of Type 2 Diabetes")
    elif disease_id == "ad" and lifestyle.family_history_ad:
        fam_mod = 1.30
        drivers.append("Family history of Alzheimer's Dementia")
    mults["family_history"] = fam_mod

    # Aggregate lifestyle relative risk using geometric weighting
    log_rr = (
        0.22 * math.log(mults["bmi"]) +
        0.25 * math.log(mults["smoking"]) +
        0.18 * math.log(mults["physical_activity"]) +
        0.15 * math.log(mults["diet"]) +
        0.20 * math.log(mults["blood_pressure"]) +
        0.10 * math.log(mults["sleep"]) +
        0.10 * math.log(mults["alcohol"]) +
        0.15 * math.log(mults["family_history"])
    )
    lifestyle_rr = math.exp(log_rr)

    return round(lifestyle_rr, 3), mults, drivers

def fuse_genetic_and_lifestyle_risk(
    disease_id: str,
    prs_standardized_z: float,
    prs_percentile: float,
    lifestyle: LifestyleFactors
) -> Dict[str, Any]:
    """
    Executes late-fusion between genetic PRS and lifestyle covariates.
    Returns fused relative risk, 10-year absolute risk, risk category, and percentage attribution.
    """
    weights = HERITABILITY_WEIGHTS.get(disease_id, {"genetic": 0.50, "lifestyle": 0.50})
    w_gen = weights["genetic"]
    w_life = weights["lifestyle"]

    # 1. Genetic Relative Risk from standardized Z-score
    # Standard PRS hazard ratio per standard deviation is typically ~1.4 - 1.7 in GWAS
    per_sd_hazard = 1.55 if disease_id in ("cad", "t2d") else 1.45
    genetic_rr = math.exp(math.log(per_sd_hazard) * prs_standardized_z)
    genetic_rr = max(0.20, min(5.0, genetic_rr))

    # 2. Lifestyle Relative Risk
    lifestyle_rr, mults, drivers = compute_lifestyle_multipliers(lifestyle, disease_id)

    # 3. Fused Combined Relative Risk
    fused_rr = (genetic_rr ** w_gen) * (lifestyle_rr ** w_life)
    fused_rr = max(0.15, min(6.0, fused_rr))

    # 4. 10-Year Absolute Risk
    baseline_ar = BASELINE_10YR_RISK.get(disease_id, 0.08)
    fused_ar = min(0.90, max(0.01, baseline_ar * fused_rr))

    # 5. Risk Category Classification
    if fused_ar < 0.06:
        category = "Low"
    elif fused_ar < 0.12:
        category = "Average"
    elif fused_ar < 0.22:
        category = "Elevated"
    else:
        category = "High"

    # 6. Proportional Variance Attribution
    log_gen_dev = abs(math.log(max(0.01, genetic_rr)))
    log_life_dev = abs(math.log(max(0.01, lifestyle_rr)))
    total_dev = log_gen_dev + log_life_dev

    if total_dev > 0:
        gen_pct = round((log_gen_dev / total_dev) * 100.0, 1)
        life_pct = round(100.0 - gen_pct, 1)
    else:
        gen_pct = 50.0
        life_pct = 50.0

    # Format key genetic drivers
    if prs_percentile >= 80.0:
        drivers.insert(0, f"High genetic risk score ({prs_percentile:.1f}th percentile)")
    elif prs_percentile <= 20.0:
        drivers.append(f"Protective genetic profile ({prs_percentile:.1f}th percentile)")

    return {
        "fused_relative_risk": round(fused_rr, 2),
        "fused_absolute_risk_10yr": round(fused_ar, 3),
        "risk_category": category,
        "genetic_contribution_pct": gen_pct,
        "lifestyle_contribution_pct": life_pct,
        "lifestyle_multipliers": mults,
        "key_risk_drivers": drivers
    }
