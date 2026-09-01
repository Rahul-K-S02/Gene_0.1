# GeneRisk — AI-Powered Genomic Risk Intelligence System

GeneRisk is a full-stack, cloud-architected genomic risk intelligence platform. It converts raw genomic data (VCF files or pre-filtered panels) and physiological lifestyle factors into an explainable, multi-disease risk assessment report.

The system combines statistical genetics (P+T Polygenic Risk Scores), machine learning (XGBoost + SHAP feature attribution), Pharmacogenomics (PharmGKB drug-gene sensitivity alerts), and grounded conversational AI (Qdrant + FastEmbed + Groq LLaMA 3.1).

---

## Key Features

### 1. Defensible Statistical Genetics (P+T PRS)
- **$P+T$ (Clumping + Thresholding)**: Genomic distance-based clumping (250kb window) prunes redundant correlated variants to lead SNPs ($p < 5 \times 10^{-8}$).
- **Allele-Frequency Standardization**: Each SNP's raw dosage is standardized against true population Minor Allele Frequencies (MAF):
  $$z_i = \frac{\text{dosage}_i - 2 \cdot \text{maf}_i}{\sqrt{2 \cdot \text{maf}_i \cdot (1 - \text{maf}_i)}}$$
- **Analytic Normal CDF Percentiles**: Risk is computed using the exact normal cumulative distribution function $\Phi(Z)$, returning true population percentiles ($0.1\% - 99.9\%$).
- **Missing SNP Neutral Imputation**: Unobserved panel variants are imputed to population expectation ($z_i = 0$), avoiding arbitrary inflation.

### 2. Multi-Disease Coverage & Heritability Weights
Evaluates 5 distinct polygenic disease panels with empirical heritability late-fusion weighting:
1. **Coronary Artery Disease (CAD)** (*9p21.3 / CDKN2A/B, APOB, LPA, PCSK9, KIF6*)
2. **Type 2 Diabetes (T2D)** (*TCF7L2, KCNJ11, PPARG, FTO, SLC30A8*)
3. **Alzheimer's Disease (AD)** (*APOE $\epsilon 4$/$\epsilon 2$, CLU, CR1, BIN1*)
4. **Essential Hypertension (HTN)** (*AGT, NOS3, AGTR1, ATP2B1*)
5. **Breast Cancer Polygenic Risk** (*FGFR2, TOX3, MAP3K1, 8q24*)

### 3. Pharmacogenomics (PharmGKB) & ClinVar Annotations
- Actionable drug-gene interaction warnings (*CYP2C19* & Clopidogrel resistance, *SLCO1B1* & Statin myopathy, *VKORC1/CYP2C9* & Warfarin dosage, *DPYD* & Fluoropyrimidine toxicity).
- High-penetrance monogenic variant flags (*BRCA1/2*, *LDLR*, *APOE*, *MYH7*).

### 4. Real XGBoost Models & SHAP Explainability
- Trained `XGBClassifier` models with `shap.TreeExplainer` providing signed Shapley impact attributions for both genetic and lifestyle covariates.
- Transparent mode indicator (`real_shap` vs `approximate_linear`).
- In-memory matplotlib waterfall & force plot generation returned as Base64 PNG.

### 5. Grounded RAG Clinical Narrative (Qdrant + FastEmbed + Groq)
- Vector similarity retrieval over clinical guidelines (AHA, ADA, ESC, NIA, CPIC, DPP).
- Ultra-low RAM embedding engine with `fastembed` (`bge-small-en-v1.5` ONNX).
- Interactive conversational follow-up Q&A modal (`POST /api/v1/chat`).

### 6. Interactive "What-If" Lifestyle Risk Simulator
- Live reactive sliders (BMI, smoking cessation, aerobic activity, Mediterranean diet, blood pressure) recompute fused absolute risk in real time, demonstrating how behavioral changes mitigate inherited polygenic hazard.

### 7. Zero-Dependency Standalone Edge Preprocessor (`generisk_edge.py`)
- Streams 13GB–25GB whole-genome VCF files line-by-line in $O(1)$ constant memory (<30MB RAM).
- Extracts only target rsID dosages, outputting a tiny (<50KB) JSON payload that preserves genomic privacy and uploads in milliseconds.

---

## Measured Experimental Evaluation

All reported metrics are measured directly by executing the test scripts in this repository:

### Model Discrimination (XGBoost 5-Fold Cross-Validation)
| Disease Condition | Test Set ROC-AUC | 5-Fold CV Mean ROC-AUC | Test Accuracy | Brier Calibration Score |
|---|---|---|---|---|
| **Coronary Artery Disease (CAD)** | **0.6276** | **0.6916 ± 0.0258** | **67.4%** | **0.1969** |
| **Type 2 Diabetes (T2D)** | **0.6865** | **0.7113 ± 0.0131** | **66.9%** | **0.1959** |
| **Alzheimer's Disease (AD)** | **0.6866** | **0.6918 ± 0.0361** | **71.2%** | **0.1933** |
| **Hypertension (HTN)** | **0.6388** | **0.6670 ± 0.0173** | **69.8%** | **0.1897** |
| **Breast Cancer** | **0.6651** | **0.6736 ± 0.0157** | **68.0%** | **0.1977** |

### RAG Medical Factuality Benchmark
- **Groundedness Score**: **28.6%**
- **Medical Contradiction / Hallucination Rate**: **0.0%** (Zero factual contradictions across all guideline propositions)
- **Citation Precision**: **100.0%**

---

## Project Structure

```
generisk/
├── backend/
│   ├── app/
│   │   ├── config.py                 # App settings & fallback configs
│   │   ├── database.py               # Turso libSQL client with SQLite fallback
│   │   ├── schemas.py                # Pydantic v2 data models
│   │   ├── vcf_parser.py             # Ephemeral streaming VCF parser
│   │   ├── prs_engine.py             # P+T standardized PRS with normal CDF
│   │   ├── clinvar_lookup.py         # ClinVar pathogenic variant annotator
│   │   ├── pharmgkb_lookup.py        # PharmGKB drug-gene annotator
│   │   ├── lifestyle_fusion.py       # Multi-factor late-fusion risk engine
│   │   ├── shap_explainer.py         # XGBoost loader + SHAP TreeExplainer
│   │   ├── rag_pipeline.py           # Qdrant + FastEmbed + Groq LLaMA 3.1
│   │   ├── report_generator.py       # In-memory ReportLab PDF generator
│   │   └── main.py                   # FastAPI application & routes
│   ├── models/                       # Trained XGBoost models & explainers
│   ├── tests/                        # Pytest suite (15 unit & integration tests)
│   └── requirements.txt
│
├── edge_client/
│   ├── generisk_edge.py              # Zero-dependency streaming CLI preprocessor
│   └── README.md
│
├── scripts/
│   ├── setup_db.py                   # Database table provisioning & seed data
│   ├── import_real_datasets.py       # P+T clumping verification script
│   ├── generate_synthetic_cohort.py  # Semi-synthetic training cohort generator
│   ├── train_shap_models.py          # XGBoost training & evaluation pipeline
│   ├── evaluate_rag_groundedness.py  # RAG hallucination benchmark
│   └── setup_qdrant_collection.py    # Vector store setup & indexing
│
└── frontend/                         # Next.js 14 App Router dashboard
```

---

## Quick Start & Running Locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Initialize database, cohorts, and trained models:
python ../scripts/setup_db.py
python ../scripts/generate_synthetic_cohort.py
python ../scripts/train_shap_models.py

# Run the backend API server:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your web browser.

### 3. Running Automated Tests
```bash
cd backend
pytest -v
```

### 4. Running the Standalone Edge Preprocessor
```bash
python edge_client/generisk_edge.py my_genome.vcf.gz
```
