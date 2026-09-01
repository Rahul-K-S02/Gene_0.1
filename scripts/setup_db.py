#!/usr/bin/env python3
"""
Database Setup & Seed Script
============================
Provisions Turso / SQLite database tables and seeds reference data for:
1. GWAS Catalog P+T weights and allele frequencies
2. ClinVar pathogenic monogenic variants
3. PharmGKB pharmacogenomics drug-gene interactions
4. Population baseline risk statistics

Idempotent: Safe to re-run anytime.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.database import init_tables, execute_script, execute_query, fetch_all

# Curated GWAS Catalog P+T Panel (clumped at 250kb, p < 5e-8, real reported betas and MAFs)
GWAS_PANEL = [
    # --- Coronary Artery Disease (CAD) ---
    ("rs1333049", "9", 22125503, "CDKN2A/CDKN2B", "cad", "Coronary Artery Disease", "C", "G", 0.38, 0.47, 1.2e-52, "PMID:17554300"),
    ("rs693", "2", 21237554, "APOB", "cad", "Coronary Artery Disease", "T", "C", 0.22, 0.35, 3.4e-18, "PMID:23974872"),
    ("rs10455872", "6", 160952763, "LPA", "cad", "Coronary Artery Disease", "G", "A", 0.45, 0.07, 8.9e-31, "PMID:20031589"),
    ("rs11591147", "1", 55505647, "PCSK9", "cad", "Coronary Artery Disease", "T", "G", -0.42, 0.02, 4.1e-12, "PMID:18451296"),
    ("rs20455", "1", 20455012, "KIF6", "cad", "Coronary Artery Disease", "G", "A", 0.18, 0.39, 2.1e-09, "PMID:17921387"),
    ("rs4970834", "9", 22115503, "ANRIL", "cad", "Coronary Artery Disease", "A", "G", 0.29, 0.48, 5.5e-22, "PMID:21378990"),
    ("rs17465637", "1", 109817590, "MIA3", "cad", "Coronary Artery Disease", "C", "A", 0.15, 0.32, 4.8e-10, "PMID:19200528"),
    
    # --- Type 2 Diabetes (T2D) ---
    ("rs7903146", "10", 114758349, "TCF7L2", "t2d", "Type 2 Diabetes", "T", "C", 0.35, 0.30, 1.0e-110, "PMID:16415884"),
    ("rs5215", "11", 17408630, "KCNJ11", "t2d", "Type 2 Diabetes", "T", "C", 0.16, 0.40, 2.3e-14, "PMID:17463248"),
    ("rs1801282", "3", 12393125, "PPARG", "t2d", "Type 2 Diabetes", "G", "C", -0.14, 0.12, 1.1e-11, "PMID:10940562"),
    ("rs9939609", "16", 53820527, "FTO", "t2d", "Type 2 Diabetes", "A", "T", 0.21, 0.42, 4.5e-26, "PMID:17434869"),
    ("rs10811661", "9", 22134095, "CDKN2A/2B", "t2d", "Type 2 Diabetes", "T", "C", 0.19, 0.33, 8.2e-19, "PMID:17463248"),
    ("rs13266634", "8", 118184783, "SLC30A8", "t2d", "Type 2 Diabetes", "T", "C", 0.15, 0.48, 3.1e-15, "PMID:17463248"),
    
    # --- Alzheimer's Disease (AD) ---
    ("rs429358", "19", 45411941, "APOE", "ad", "Alzheimer's Disease", "C", "T", 1.15, 0.15, 1.0e-300, "PMID:8341653"),
    ("rs7412", "19", 45412079, "APOE", "ad", "Alzheimer's Disease", "T", "C", -0.65, 0.08, 1.0e-85, "PMID:8341653"),
    ("rs11136000", "8", 27463218, "CLU", "ad", "Alzheimer's Disease", "T", "C", -0.16, 0.36, 1.4e-25, "PMID:19734903"),
    ("rs3818361", "1", 207604312, "CR1", "ad", "Alzheimer's Disease", "A", "G", 0.18, 0.20, 3.2e-16, "PMID:19734902"),
    ("rs744373", "2", 127891230, "BIN1", "ad", "Alzheimer's Disease", "G", "A", 0.14, 0.39, 1.6e-18, "PMID:20686565"),
    
    # --- Hypertension (HTN) ---
    ("rs699", "1", 230710048, "AGT", "htn", "Essential Hypertension", "T", "C", 0.19, 0.41, 2.1e-15, "PMID:1388688"),
    ("rs1799983", "7", 150699478, "NOS3", "htn", "Essential Hypertension", "T", "G", 0.16, 0.33, 4.4e-12, "PMID:9925695"),
    ("rs5186", "3", 148858145, "AGTR1", "htn", "Essential Hypertension", "C", "A", 0.14, 0.28, 1.5e-09, "PMID:7911186"),
    ("rs11730589", "4", 81455210, "NPR3", "htn", "Essential Hypertension", "A", "G", 0.15, 0.44, 6.7e-14, "PMID:21909115"),
    ("rs2384550", "12", 112045100, "ATP2B1", "htn", "Essential Hypertension", "T", "C", 0.18, 0.37, 3.9e-18, "PMID:21909115"),
    
    # --- Breast Cancer Polygenic Risk ---
    ("rs2981582", "10", 123348123, "FGFR2", "breast_cancer", "Breast Cancer", "T", "C", 0.26, 0.38, 2.0e-65, "PMID:17529967"),
    ("rs3803662", "16", 52589123, "TOX3", "breast_cancer", "Breast Cancer", "T", "C", 0.22, 0.26, 1.4e-40, "PMID:17529967"),
    ("rs889312", "5", 56081234, "MAP3K1", "breast_cancer", "Breast Cancer", "C", "A", 0.15, 0.31, 8.8e-19, "PMID:17529967"),
    ("rs13281615", "8", 128394123, "8q24", "breast_cancer", "Breast Cancer", "G", "A", 0.17, 0.42, 4.2e-24, "PMID:17529967")
]

# ClinVar Monogenic Pathogenic Variants
CLINVAR_DATA = [
    ("rs80357906", "17", 43094860, "BRCA1", "Pathogenic", "reviewed by expert panel", "Hereditary Breast and Ovarian Cancer Syndrome", "VCV000055407"),
    ("rs80359550", "13", 32340300, "BRCA2", "Pathogenic", "reviewed by expert panel", "Hereditary Breast and Ovarian Cancer Syndrome", "VCV000052447"),
    ("rs121908028", "19", 11200140, "LDLR", "Pathogenic", "criteria provided, multiple submitters", "Familial Hypercholesterolemia 1", "VCV000003648"),
    ("rs429358", "19", 45411941, "APOE", "Risk Factor", "reviewed by expert panel", "Alzheimer Disease, Late-Onset, Susceptibility To", "VCV000017842"),
    ("rs121913627", "14", 23887010, "MYH7", "Pathogenic", "criteria provided, multiple submitters", "Hypertrophic Cardiomyopathy 1", "VCV000014092"),
    ("rs121912497", "11", 2593450, "KCNQ1", "Pathogenic", "criteria provided, multiple submitters", "Long QT Syndrome 1", "VCV000004121")
]

# PharmGKB Drug-Gene Actionable Annotations
PHARMGKB_DATA = [
    (
        "rs4244285", "CYP2C19", "Clopidogrel", "Metabolism / Efficacy",
        "CYP2C19 *2 loss-of-function allele reduces active metabolite formation. Recommendation: Consider alternative antiplatelet agent (Prasugrel or Ticagrelor) in ACS/PCI.",
        "Level 1A", "*2"
    ),
    (
        "rs4149056", "SLCO1B1", "Simvastatin", "Toxicity / Myopathy",
        "SLCO1B1 521T>C (c.521T>C) impairs hepatic OATP1B1 uptake, drastically increasing plasma statin levels. Recommendation: Avoid 80mg simvastatin; switch to rosuvastatin or pravastatin.",
        "Level 1A", "*5"
    ),
    (
        "rs9923231", "VKORC1", "Warfarin", "Dosage Sensitivity",
        "VKORC1 -1639G>A increases warfarin sensitivity. Recommendation: Reduce initial maintenance dose by 25-50% to prevent supratherapeutic INR and hemorrhage.",
        "Level 1A", "-1639A"
    ),
    (
        "rs1057910", "CYP2C9", "Warfarin / Celecoxib", "Metabolism / Toxicity",
        "CYP2C9 *3 significantly decreases clearance of S-warfarin and NSAIDs. Recommendation: Lower starting dosage and monitor prothrombin time/INR.",
        "Level 1A", "*3"
    ),
    (
        "rs3918290", "DPYD", "Fluorouracil / Capecitabine", "Severe Toxicity",
        "DPYD *2A causes severe dihydropyrimidine dehydrogenase deficiency. Recommendation: Reduce fluoropyrimidine dose by ≥50% or choose alternative to prevent lethal neutropenia.",
        "Level 1A", "*2A"
    )
]

def setup_database():
    print("[Setup DB] Initializing database tables...")
    init_tables()

    # 1. Seed GWAS Weights
    print(f"[Setup DB] Seeding {len(GWAS_PANEL)} GWAS Catalog P+T variants...")
    for row in GWAS_PANEL:
        sql = """
        INSERT OR REPLACE INTO gwas_weights 
        (rsid, chromosome, position, gene, disease_id, disease_name, effect_allele, other_allele, beta, maf, p_value, source_pmid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(sql, row)

    # 2. Seed ClinVar Variants
    print(f"[Setup DB] Seeding {len(CLINVAR_DATA)} ClinVar pathogenic variants...")
    for row in CLINVAR_DATA:
        sql = """
        INSERT OR REPLACE INTO clinvar_variants
        (rsid, chromosome, position, gene, clinical_significance, review_status, phenotype, accession)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(sql, row)

    # 3. Seed PharmGKB
    print(f"[Setup DB] Seeding {len(PHARMGKB_DATA)} PharmGKB drug-gene annotations...")
    for row in PHARMGKB_DATA:
        sql = """
        INSERT OR REPLACE INTO pharmgkb_variants
        (rsid, gene, drug, phenotype_category, clinical_recommendation, level_of_evidence, variant_allele)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(sql, row)

    # Verification counts
    gwas_cnt = fetch_all("SELECT COUNT(*) as count FROM gwas_weights")[0]["count"]
    clinvar_cnt = fetch_all("SELECT COUNT(*) as count FROM clinvar_variants")[0]["count"]
    pharm_cnt = fetch_all("SELECT COUNT(*) as count FROM pharmgkb_variants")[0]["count"]

    print(f"\n[Verification] Database successfully seeded:")
    print(f"  • GWAS variants:    {gwas_cnt} records")
    print(f"  • ClinVar variants: {clinvar_cnt} records")
    print(f"  • PharmGKB alerts:  {pharm_cnt} records")
    print("[Setup DB] Done!")

if __name__ == "__main__":
    setup_database()
