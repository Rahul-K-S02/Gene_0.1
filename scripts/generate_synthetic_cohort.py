#!/usr/bin/env python3
"""
Semi-Synthetic Cohort Generation Script
========================================
Generates realistic semi-synthetic cohorts (N=5,000 individuals per disease)
with:
1. Genotypes sampled according to Hardy-Weinberg Equilibrium (p^2, 2pq, q^2) using real GWAS Catalog MAFs.
2. Correlated physiological & lifestyle covariates (BMI, Smoking, Activity, Diet, SBP, Sleep, Alcohol, Family History).
3. Ground-truth disease binary outcomes generated via logistic link function from the true combined genetic + lifestyle hazard.

Disclaimer:
As noted in the scientific documentation, this semi-synthetic cohort serves to verify
that machine learning models (XGBoost + SHAP) correctly recover known true signals in
the data pipeline. It is not an observational clinical study.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.database import init_tables, fetch_all
from app.config import settings

def generate_cohort_for_disease(
    disease_id: str,
    n_samples: int = 5000,
    seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)
    
    # 1. Fetch disease SNPs
    init_tables()
    query = "SELECT rsid, gene, beta, maf FROM gwas_weights WHERE disease_id = ?"
    snps = fetch_all(query, (disease_id,))
    if not snps:
        print(f"Warning: No SNPs found for {disease_id}")
        return pd.DataFrame()

    # 2. Sample Genotypes under Hardy-Weinberg Equilibrium
    # P(dosage = 0) = (1-maf)^2
    # P(dosage = 1) = 2 * maf * (1-maf)
    # P(dosage = 2) = maf^2
    raw_prs = np.zeros(n_samples, dtype=np.float32)
    mu_pop = 0.0
    var_pop = 0.0

    for snp in snps:
        maf = float(snp["maf"])
        beta = float(snp["beta"])
        
        p0 = (1.0 - maf) ** 2
        p1 = 2.0 * maf * (1.0 - maf)
        p2 = maf ** 2
        
        dosages = np.random.choice([0.0, 1.0, 2.0], size=n_samples, p=[p0, p1, p2])
        raw_prs += beta * dosages
        
        mu_pop += beta * (2.0 * maf)
        var_pop += (beta ** 2) * (2.0 * maf * (1.0 - maf))

    sigma_pop = np.sqrt(var_pop) if var_pop > 0 else 1.0
    prs_z = (raw_prs - mu_pop) / sigma_pop

    # 3. Sample Correlated Lifestyle & Clinical Covariates
    age = np.random.normal(loc=52.0, scale=12.0, size=n_samples).clip(25, 85)
    bmi = np.random.normal(loc=27.2, scale=4.8, size=n_samples).clip(17.0, 48.0)
    
    # Smoking: 0=never (60%), 1=former (25%), 2=current (15%)
    smoking = np.random.choice([0, 1, 2], size=n_samples, p=[0.60, 0.25, 0.15])
    
    # Physical activity (exponential distribution, hrs/week)
    activity = np.random.exponential(scale=2.2, size=n_samples).clip(0.0, 20.0)
    
    # Diet score (0-10, mean ~6)
    diet = np.random.binomial(n=10, p=0.6, size=n_samples)
    
    # Systolic blood pressure (correlated slightly with BMI and age)
    sbp_base = 110.0 + 0.3 * (age - 40.0) + 0.8 * (bmi - 25.0)
    sbp = (sbp_base + np.random.normal(loc=0, scale=10.0, size=n_samples)).clip(90, 200)
    
    # Sleep hours
    sleep = np.random.normal(loc=7.2, scale=1.1, size=n_samples).clip(4.0, 11.0)
    
    # Alcohol drinks per week
    alcohol = np.random.exponential(scale=3.5, size=n_samples).clip(0.0, 40.0)
    
    # Family history (binary 20% prevalence)
    family_hist = np.random.binomial(n=1, p=0.20, size=n_samples)

    # 4. Generate Ground-Truth Disease Binary Labels via Logistic Link Function
    # Logit = intercept + beta_gen * prs_z + sum(beta_life * covar) + noise
    if disease_id == "cad":
        logit = (
            -2.4 +
            0.65 * prs_z +
            0.04 * (age - 50) +
            0.05 * (bmi - 25) +
            0.55 * (smoking == 2) + 0.20 * (smoking == 1) -
            0.12 * activity -
            0.08 * (diet - 5) +
            0.025 * (sbp - 120) +
            0.40 * family_hist +
            np.random.normal(0, 0.4, size=n_samples)
        )
    elif disease_id == "t2d":
        logit = (
            -2.2 +
            0.60 * prs_z +
            0.03 * (age - 50) +
            0.12 * (bmi - 25) +
            0.25 * (smoking == 2) -
            0.15 * activity -
            0.10 * (diet - 5) +
            0.015 * (sbp - 120) +
            0.45 * family_hist +
            np.random.normal(0, 0.4, size=n_samples)
        )
    else:
        # Default trait model
        logit = (
            -2.5 +
            0.70 * prs_z +
            0.05 * (age - 50) +
            0.04 * (bmi - 25) +
            0.30 * (smoking == 2) -
            0.10 * activity +
            0.35 * family_hist +
            np.random.normal(0, 0.4, size=n_samples)
        )

    prob = 1.0 / (1.0 + np.exp(-logit))
    outcome = np.random.binomial(1, prob)

    df = pd.DataFrame({
        "prs_z": prs_z,
        "age": age,
        "bmi": bmi,
        "smoking": smoking,
        "activity": activity,
        "diet": diet,
        "sbp": sbp,
        "sleep": sleep,
        "alcohol": alcohol,
        "family_history": family_hist,
        "outcome": outcome,
        "true_prob": prob
    })

    print(f"Generated cohort for {disease_id}: {n_samples} samples | Disease Prevalence: {df['outcome'].mean()*100:.1f}%")
    return df

def generate_all_cohorts():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    diseases = ["cad", "t2d", "ad", "htn", "breast_cancer"]
    
    print("\n--- Generating Semi-Synthetic Multi-Disease Cohorts ---")
    for d in diseases:
        df = generate_cohort_for_disease(d, n_samples=5000, seed=42 + hash(d) % 1000)
        out_path = settings.DATA_DIR / f"cohort_{d}.csv"
        df.to_csv(out_path, index=False)
        print(f"  [OK] Saved {out_path.name}")
    print("[Complete] All cohorts generated successfully.\n")

if __name__ == "__main__":
    generate_all_cohorts()
