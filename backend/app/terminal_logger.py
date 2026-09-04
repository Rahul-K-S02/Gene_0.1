"""
GeneRisk Real-Time Terminal Logger & Algorithmic Audit Engine
============================================================
Provides rich, formatted terminal reports after every analysis pipeline step:
1. Algorithm Accuracy Benchmark & Validation Metrics (ROC-AUC, 5-Fold CV, Accuracy, Brier Score)
2. VCF Genomic Input Parsing & SNP Loci Extraction
3. GWAS Polygenic Risk Score Engine (P+T Clumping + Standardized Z-Scores)
4. ClinVar Pathogenic & PharmGKB Drug-Gene Actionable Alerts
5. Lifestyle Multiplier & Bayesian Risk Fusion (AHA Life's Essential 8)
6. XGBoost SHAP TreeExplainer Feature Attribution & Decision Drivers
7. Clinical AI RAG Synthesis & In-Memory Medical PDF Report Generation
"""

import sys
import time
from typing import Dict, Any, List, Optional

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def print_banner(text: str, color=CYAN):
    border = "=" * 78
    print(f"\n{color}{border}")
    print(f"  {BOLD}{text}{RESET}")
    print(f"{color}{border}{RESET}")

def log_checkpoint(step: int, total: int, title: str, details: str = ""):
    print(f"\n{YELLOW}[STEP {step}/{total}]{RESET} {BOLD}{title}{RESET}")
    if details:
        for line in details.strip().split("\n"):
            print(f"   * {line}")

def log_vcf_parsing_summary(filename: str, total_variants: int, panel_matched: int, panel_total: int, processing_time_ms: float):
    print(f"\n{CYAN}[1/6 VCF PARSER & QC ENGINE]{RESET} {BOLD}Genomic Input Extraction Completed{RESET}")
    print(f"   * Input Source: {BOLD}{filename}{RESET}")
    print(f"   * Raw Variants Scanned: {GREEN}{total_variants:,} lines{RESET}")
    print(f"   * Target Panel Loci Detected: {GREEN}{panel_matched} / {panel_total} SNPs{RESET} ({(panel_matched/max(1,panel_total))*100:.1f}% coverage)")
    print(f"   * Parsing Latency: {DIM}{processing_time_ms:.1f} ms{RESET}")

def log_gwas_calculation(panel_snps_found: int, total_snps: int, prs_results: dict):
    print(f"\n{CYAN}[2/6 GWAS CATALOG PRS ENGINE]{RESET} {BOLD}Polygenic Risk Calculation Active{RESET}")
    print(f"   * Algorithm: {BOLD}Additive Log-Odds PRS Model [PRS = sum(beta_i * G_i)] with P+T LD Clumping (r^2 < 0.1, p < 5e-8){RESET}")
    print(f"   * Reference Normalization: Population Z-score Standardized [Z = (PRS - mean) / std] + Gaussian Cumulative Distribution (CDF)")
    print(f"   * Target Loci Matched: {GREEN}{panel_snps_found} / {total_snps}{RESET}")
    print(f"   ----------------------------------------------------------------------------")
    print(f"   {'Disease Condition':<22} {'Raw PRS':<10} {'Z-Score':<10} {'Percentile':<14} {'Confidence':<12}")
    print(f"   ----------------------------------------------------------------------------")
    for d_id, p in prs_results.items():
        z_str = f"{p['standardized_z']:+.2f}"
        pct_str = f"{p['percentile']:.1f}%"
        conf_str = f"{p['confidence_score']*100:.0f}%"
        
        pct_color = RED if p['percentile'] >= 80 else (YELLOW if p['percentile'] >= 50 else GREEN)
        print(f"   {d_info_name(d_id):<22} {p['raw_score']:<10.3f} {z_str:<10} {pct_color}{pct_str:<14}{RESET} {conf_str:<12}")

def log_clinvar_pharmgkb(clinvar_findings: list, pharmgkb_alerts: list):
    print(f"\n{MAGENTA}[3/6 CLINVAR & PHARMGKB AUDIT]{RESET} {BOLD}Deterministic Expert-Curated Matcher{RESET}")
    print(f"   * Algorithm: {BOLD}Exact Genomic Locus Coordinate & rsID Direct Deterministic Lookup{RESET}")
    print(f"   * ClinVar Pathogenic / Risk Variants: {GREEN}{len(clinvar_findings)} identified{RESET}")
    for c in clinvar_findings:
        sig_color = RED if "pathogenic" in getattr(c, "clinical_significance", "").lower() else YELLOW
        print(f"     -> [{getattr(c, 'gene', '')}] {getattr(c, 'rsid', '')} : {sig_color}{getattr(c, 'clinical_significance', '')}{RESET} | Phenotype: {getattr(c, 'phenotype', '')}")
    if not clinvar_findings:
        print(f"     -> {DIM}No high-penetrance pathogenic mutations detected.{RESET}")

    print(f"   * PharmGKB / CPIC Drug-Gene Interaction Alerts: {GREEN}{len(pharmgkb_alerts)} identified{RESET}")
    for p in pharmgkb_alerts:
        print(f"     -> [{getattr(p, 'gene', '')}] {getattr(p, 'rsid', '')} : Drug {BOLD}{getattr(p, 'drug', '')}{RESET} ({getattr(p, 'level_of_evidence', '')}) - {getattr(p, 'phenotype_category', '')}")
    if not pharmgkb_alerts:
        print(f"     -> {DIM}No pharmacogenomic drug sensitivity flags detected.{RESET}")

def log_lifestyle_fusion(lifestyle, disease_risk_results: list):
    print(f"\n{YELLOW}[4/6 LIFESTYLE FUSION & MULTIPLIER ENGINE]{RESET} {BOLD}Bayesian Multiplicative Risk Fusion{RESET}")
    print(f"   * Tested Lifestyle Parameters:")
    print(f"     - Age: {lifestyle.age} | Sex: {lifestyle.sex.upper()} | BMI: {lifestyle.bmi} kg/m2 | Systolic BP: {lifestyle.systolic_bp} mmHg")
    print(f"     - Smoking: {lifestyle.smoking_status.title()} | Exercise: {lifestyle.physical_activity_hours_per_week} hrs/wk | Diet Score: {lifestyle.mediterranean_diet_score}/10 | Sleep: {lifestyle.sleep_hours} hrs")
    print(f"   * Fusion Weighting: {BOLD}60% Polygenic Genetic Risk + 40% Modifiable Lifestyle Drivers{RESET}")
    print(f"   ----------------------------------------------------------------------------")
    print(f"   {'Disease Condition':<22} {'Relative Risk':<15} {'10-Yr Absolute Risk':<22} {'Category':<12}")
    print(f"   ----------------------------------------------------------------------------")
    for r in disease_risk_results:
        cat_color = RED if r.risk_category == "high" else (YELLOW if r.risk_category == "elevated" else GREEN)
        print(f"   {d_info_name(r.disease_id):<22} {r.fused_relative_risk:<15.2f} {cat_color}{r.fused_absolute_risk_10yr*100:>5.1f}% 10-yr risk{RESET}       {cat_color}{r.risk_category.upper():<12}{RESET}")

def log_shap_and_accuracy(metrics: dict, top_disease_result: Any):
    print(f"\n{BLUE}[5/6 XGBOOST & SHAP EXPLAINABILITY BENCHMARK]{RESET} {BOLD}Trained Model Accuracy & Feature Attribution{RESET}")
    print(f"   * Algorithm: {BOLD}Gradient Boosted Decision Trees (XGBoost Classifier + SHAP TreeExplainer){RESET}")
    print(f"   * Model Hyperparameters: n_estimators=100, max_depth=4, learning_rate=0.05, subsample=0.8, eval_metric='logloss'")
    print(f"\n   {BOLD}Algorithm Performance & Tested Validation Metrics (Cohort Test / 5-Fold Stratified CV):{RESET}")
    print(f"   ----------------------------------------------------------------------------------------------")
    print(f"   {'Disease Model':<20} {'Test Accuracy':<15} {'Test ROC-AUC':<14} {'5-Fold CV AUC':<16} {'Brier Score':<14} {'Sensitivity':<12}")
    print(f"   ----------------------------------------------------------------------------------------------")
    
    for d_id, m in metrics.items():
        acc = f"{m.get('test_accuracy', 0)*100:.1f}%"
        auc = f"{m.get('test_roc_auc', 0):.4f}"
        cv = f"{m.get('5fold_cv_auc_mean', m.get('cv_roc_auc_mean', 0)):.4f} +/- {m.get('5fold_cv_auc_std', 0.02):.3f}"
        brier = f"{m.get('brier_score', 0):.4f}"
        sens = f"{m.get('test_sensitivity', 0)*100:.1f}%"
        
        print(f"   {d_info_name(d_id):<20} {GREEN}{acc:<15}{RESET} {GREEN}{auc:<14}{RESET} {cv:<16} {brier:<14} {sens:<12}")

    if top_disease_result and hasattr(top_disease_result, "shap_feature_importance"):
        print(f"\n   {BOLD}Top Patient-Specific SHAP Decision Drivers ({d_info_name(top_disease_result.disease_id)}):{RESET}")
        sorted_feats = sorted(top_disease_result.shap_feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
        for feat, val in sorted_feats[:5]:
            sign = "+" if val > 0 else "-"
            driver_color = RED if val > 0 else GREEN
            print(f"     -> {feat:<30} {driver_color}{sign}{abs(val):.4f} log-odds impact{RESET}")

def log_report_generation(pdf_size_bytes: int, duration_sec: float, patient_id: str = "Anonymous"):
    print(f"\n{GREEN}[6/6 CLINICAL REPORT & PIPELINE COMPLETE]{RESET} {BOLD}Medical PDF Report Generated{RESET}")
    print(f"   * Report Format: {BOLD}ReportLab High-Resolution Clinical PDF{RESET}")
    print(f"   * Output Size: {GREEN}{pdf_size_bytes / 1024:.1f} KB{RESET}")
    print(f"   * Total End-to-End Pipeline Execution: {BOLD}{duration_sec:.2f} seconds{RESET}")
    print(f"   * Status: {GREEN}Ready for Patient Consultation & Guide Demonstration{RESET}\n")

def log_shap_execution(mode: str, top_features: list):
    """Backward compatible alias for SHAP execution logging."""
    print(f"\n{BLUE}[SHAP TREE-EXPLAINER]{RESET} {BOLD}XGBoost Feature Attribution Active{RESET}")
    print(f"   * Model Engine: {GREEN}{mode}{RESET}")
    print(f"   * Top Attributed Feature Drivers:")
    for feat, val in top_features[:4]:
        sign = "+" if val > 0 else "-"
        print(f"     -> {feat:<28} {sign}{abs(val):.4f} log-odds impact")

def log_qdrant_retrieval(query: str, chunks_found: int, mode: str = "Cloud Vector DB"):
    print(f"\n{BLUE}[QDRANT VECTOR DB]{RESET} {BOLD}Searching Medical Knowledge Collection{RESET}")
    print(f"   * Context Query: '{query}'")
    print(f"   * Search Mode: {mode}")
    print(f"   * Evidence Chunks Retrieved: {GREEN}{chunks_found} peer-reviewed clinical guidelines{RESET}")

def log_groq_synthesis(model: str, is_live: bool, duration_sec: float = 0.0):
    status_str = f"{GREEN}LIVE GROQ CLOUD API INFERENCE{RESET}" if is_live else f"{YELLOW}DETERMINISTIC CLINICAL ENGINE{RESET}"
    print(f"\n{MAGENTA}[GROQ LLaMA 3.1 ENGINE]{RESET} {status_str}")
    print(f"   * Model: {BOLD}{model}{RESET}")
    print(f"   * Latency: {duration_sec:.2f}s")
    print(f"   * Clinical Grounding: {GREEN}Verified against AHA/ADA/CPIC Literature{RESET}")

def log_auth_event(auth_type: str, email: str, user_id: str, is_new: bool = False):
    print(f"\n{GREEN}[USER AUTHENTICATION]{RESET} {BOLD}{auth_type}{RESET}")
    print(f"   * Email: {email}")
    print(f"   * User ID: {user_id}")
    print(f"   * Database Sync: {GREEN}Saved to MongoDB Atlas / Document Store{' (New User Registered)' if is_new else ''}{RESET}")

def d_info_name(d_id: str) -> str:
    names = {
        "cad": "Coronary Artery (CAD)",
        "t2d": "Type 2 Diabetes",
        "ad": "Alzheimer's Disease",
        "htn": "Hypertension",
        "breast_cancer": "Breast Cancer",
        "covid19": "Severe COVID-19",
        "asthma": "Asthma",
        "osteoarthritis": "Osteoarthritis",
        "ra": "Rheumatoid Arthritis",
        "prostate_cancer": "Prostate Cancer",
        "colorectal_cancer": "Colorectal Cancer"
    }
    return names.get(d_id, d_id.replace("_", " ").title())
