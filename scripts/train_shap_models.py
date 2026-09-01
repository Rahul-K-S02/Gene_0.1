#!/usr/bin/env python3
"""
Model Training & SHAP Explainer Generator
=========================================
Trains real XGBoost classifiers for each disease condition, computes empirical
test-set ROC-AUC evaluation metrics, and serializes trained models along with
shap.TreeExplainer instances into backend/models/.

All reported metrics are measured directly from executed code on held-out splits.
"""

import sys
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, brier_score_loss
import xgboost as xgb
import shap

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings

FEATURE_COLS = [
    "prs_z", "bmi", "smoking", "activity", "diet", "sbp", "sleep", "alcohol", "family_history"
]

def train_and_evaluate_disease(disease_id: str) -> dict:
    cohort_path = settings.DATA_DIR / f"cohort_{disease_id}.csv"
    if not cohort_path.exists():
        print(f"[Error] Cohort data missing for {disease_id} at {cohort_path}. Run generate_synthetic_cohort.py first.")
        return {}

    df = pd.read_csv(cohort_path)
    X = df[FEATURE_COLS].values
    y = df["outcome"].values

    # 80/20 Train/Test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Train XGBoost Classifier
    scale_pos = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        random_state=42,
        eval_metric="logloss"
    )
    
    model.fit(X_train, y_train)

    # Evaluate on held-out test split
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    auc = float(roc_auc_score(y_test, y_pred_proba))
    acc = float(accuracy_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    brier = float(brier_score_loss(y_test, y_pred_proba))

    # Cross-validation AUC
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
    cv_auc_mean = float(np.mean(cv_scores))
    cv_auc_std = float(np.std(cv_scores))

    # Initialize SHAP TreeExplainer
    explainer = shap.TreeExplainer(model)

    # Save artifacts
    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = settings.MODELS_DIR / f"{disease_id}_xgb.pkl"
    explainer_path = settings.MODELS_DIR / f"{disease_id}_explainer.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(explainer_path, "wb") as f:
        pickle.dump(explainer, f)

    metrics = {
        "disease_id": disease_id,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "test_roc_auc": round(auc, 4),
        "5fold_cv_auc_mean": round(cv_auc_mean, 4),
        "5fold_cv_auc_std": round(cv_auc_std, 4),
        "test_accuracy": round(acc, 4),
        "test_sensitivity": round(rec, 4),
        "test_precision": round(prec, 4),
        "brier_score": round(brier, 4)
    }

    print(f"\n[Model Trained: {disease_id.upper()}]")
    print(f"  • Test Split ROC-AUC:    {auc:.4f}")
    print(f"  • 5-Fold CV ROC-AUC:     {cv_auc_mean:.4f} ± {cv_auc_std:.4f}")
    print(f"  • Test Accuracy:         {acc*100:.1f}%")
    print(f"  • Brier Calibration:     {brier:.4f}")
    print(f"  [OK] Saved model: {model_path.name}")
    print(f"  [OK] Saved TreeExplainer: {explainer_path.name}")

    return metrics

def train_all_models():
    diseases = ["cad", "t2d", "ad", "htn", "breast_cancer"]
    all_metrics = {}

    print("\n=======================================================")
    print("  Training XGBoost Multi-Disease Models & SHAP Explainers")
    print("=======================================================")

    for d in diseases:
        res = train_and_evaluate_disease(d)
        if res:
            all_metrics[d] = res

    metrics_file = settings.MODELS_DIR / "model_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\n[Summary] All models trained and verified. Metrics logged to {metrics_file.name}\n")

if __name__ == "__main__":
    train_all_models()
