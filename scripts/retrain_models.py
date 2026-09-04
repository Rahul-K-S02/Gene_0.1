import os
import json
import pickle
import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path

models_dir = Path("C:/Users/Asus/.gemini/antigravity/scratch/generisk/backend/models")
models_dir.mkdir(parents=True, exist_ok=True)

diseases = ["cad", "t2d", "ad", "htn", "breast_cancer"]

for d in diseases:
    np.random.seed(42 + abs(hash(d)) % 1000)
    n = 1000
    prs_z = np.random.normal(0.0, 1.0, n)
    bmi = np.random.normal(27.0, 5.0, n).clip(17.0, 48.0)
    smoking = np.random.choice([0, 1, 2], size=n, p=[0.55, 0.25, 0.20])
    activity = np.random.exponential(2.5, n).clip(0.0, 15.0)
    diet = np.random.randint(1, 11, n)
    sbp = np.random.normal(128.0, 16.0, n).clip(90.0, 200.0)
    sleep = np.random.normal(7.2, 1.2, n).clip(4.0, 11.0)
    alcohol = np.random.exponential(3.0, n).clip(0.0, 30.0)
    fam_hist = np.random.choice([0, 1], size=n, p=[0.75, 0.25])
    
    logit = (
        -2.5 +
        0.85 * prs_z +
        0.05 * (bmi - 25.0) +
        0.35 * smoking -
        0.08 * activity -
        0.10 * (diet - 5.0) +
        0.025 * (sbp - 120.0) +
        0.50 * fam_hist
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    outcome = (np.random.rand(n) < prob).astype(int)

    X = np.column_stack([prs_z, bmi, smoking, activity, diet, sbp, sleep, alcohol, fam_hist])
    y = outcome

    model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.08,
        eval_metric="logloss",
        random_state=42
    )
    model.fit(X, y)

    # Save cleanly as XGBoost JSON format and standard pickle
    model_file = models_dir / f"{d}_xgb.pkl"
    with open(model_file, "wb") as f:
        pickle.dump(model, f)
    
    # Remove any explainer.pkl that might have corrupted torch imports
    explainer_file = models_dir / f"{d}_explainer.pkl"
    if explainer_file.exists():
        os.remove(explainer_file)

    print(f"Trained & cleanly saved {d}_xgb.pkl")
