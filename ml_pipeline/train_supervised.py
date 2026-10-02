"""
SIH26146 — Supervised Machine Learning Benchmark Pipeline
=========================================================
Models: Logistic Regression & Random Forest
Temporal Split:
  - TRAIN:      Steps 1 – 30
  - VALIDATION: Steps 31 – 40
  - TEST:       Steps 41 – 49 (Held-Out Evaluation)
Labels:
  - Class 1 (Illicit) vs Class 2 (Licit)
  - Class 3 (Unknown) strictly EXCLUDED from supervised training & evaluation.
"""

import os
import json
import time
import pickle
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    precision_recall_curve,
    auc,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

V1_DIR = r"C:\Users\apeksha\Downloads\archive (1)\elliptic_bitcoin_dataset"
V2_DIR = r"C:\Users\apeksha\Downloads\drive-download-20261001T200400Z-1-001"
OUTPUT_BASE = r"c:\Users\apeksha\OneDrive\Documents\GitHub\Bitcoin-transaction\models"

def run_supervised_pipeline(dataset_name, data_dir, is_v2=False):
    print(f"\n=======================================================")
    print(f"   EXECUTING SUPERVISED ML BENCHMARK: {dataset_name.upper()}")
    print(f"=======================================================")

    target_model_dir = os.path.join(OUTPUT_BASE, dataset_name)
    os.makedirs(target_model_dir, exist_ok=True)

    # 1. LOAD DATA & VERIFY SCHEMAS
    if not is_v2:
        classes_path = os.path.join(data_dir, 'elliptic_txs_classes.csv')
        features_path = os.path.join(data_dir, 'elliptic_txs_features.csv')
        df_classes = pd.read_csv(classes_path)
        class_map = {'1': 1, '2': 2, 'unknown': 3}
        df_classes['class_num'] = df_classes['class'].map(class_map).fillna(3).astype(int)

        df_features = pd.read_csv(features_path, header=None)
        tx_id_col = 'txId'
        time_step_col = 'time_step'
        df_features = df_features.rename(columns={0: tx_id_col, 1: time_step_col})
        raw_feature_cols = [c for c in df_features.columns if c not in [tx_id_col, time_step_col]]
    else:
        classes_path = os.path.join(data_dir, 'txs_classes.csv')
        features_path = os.path.join(data_dir, 'txs_features.csv')
        df_classes = pd.read_csv(classes_path)
        df_classes['class_num'] = df_classes['class'].astype(int)

        df_features = pd.read_csv(features_path)
        tx_id_col = 'txId'
        time_step_col = 'Time step'
        raw_feature_cols = [c for c in df_features.columns if c not in [tx_id_col, time_step_col]]

    df = pd.merge(df_features, df_classes[[tx_id_col, 'class_num']], on=tx_id_col, how='inner')
    df[raw_feature_cols] = df[raw_feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)

    # STRICTLY FILTER LABELED DATASET (Class 1 & Class 2 only)
    df_labeled = df[df['class_num'].isin([1, 2])].copy()
    # Binary target: 1 = Illicit, 0 = Licit
    df_labeled['target'] = (df_labeled['class_num'] == 1).astype(int)

    # 2. CHRONOLOGICAL TEMPORAL SPLIT (1-30, 31-40, 41-49)
    train_mask = df_labeled[time_step_col] <= 30
    val_mask = (df_labeled[time_step_col] >= 31) & (df_labeled[time_step_col] <= 40)
    test_mask = df_labeled[time_step_col] >= 41

    df_train = df_labeled[train_mask].copy()
    df_val = df_labeled[val_mask].copy()
    df_test = df_labeled[test_mask].copy()

    # REMOVE CONSTANT FEATURES
    variances = df_train[raw_feature_cols].var()
    active_feature_cols = variances[variances > 1e-12].index.tolist()

    scaler = StandardScaler()
    X_train = scaler.fit_transform(df_train[active_feature_cols])
    y_train = df_train['target'].values

    X_val = scaler.transform(df_val[active_feature_cols])
    y_val = df_val['target'].values

    X_test = scaler.transform(df_test[active_feature_cols])
    y_test = df_test['target'].values

    print(f"Labeled Samples: Train={len(df_train)} (Illicit={y_train.sum()}), Val={len(df_val)} (Illicit={y_val.sum()}), Test={len(df_test)} (Illicit={y_test.sum()})")

    # 3. TRAIN LOGISTIC REGRESSION
    print("\nTraining Logistic Regression (class_weight='balanced')...")
    log_reg = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    log_reg.fit(X_train, y_train)

    val_probs_lr = log_reg.predict_proba(X_val)[:, 1]
    test_probs_lr = log_reg.predict_proba(X_test)[:, 1]

    # Tune threshold on Validation set to maximize F1 score
    best_thresh_lr = 0.5
    best_f1_lr = -1.0
    for t in np.linspace(0.05, 0.95, 91):
        f1_t = f1_score(y_val, (val_probs_lr >= t).astype(int), zero_division=0)
        if f1_t > best_f1_lr:
            best_f1_lr = f1_t
            best_thresh_lr = t

    test_preds_lr = (test_probs_lr >= best_thresh_lr).astype(int)
    roc_lr = float(roc_auc_score(y_test, test_probs_lr))
    p_prec_lr, p_rec_lr, _ = precision_recall_curve(y_test, test_probs_lr)
    pr_auc_lr = float(auc(p_rec_lr, p_prec_lr))
    prec_lr = float(precision_score(y_test, test_preds_lr, zero_division=0))
    rec_lr = float(recall_score(y_test, test_preds_lr, zero_division=0))
    f1_lr = float(f1_score(y_test, test_preds_lr, zero_division=0))
    cm_lr = confusion_matrix(y_test, test_preds_lr).tolist()

    print(f"Logistic Regression Test Metrics: ROC-AUC={roc_lr:.4f}, PR-AUC={pr_auc_lr:.4f}, F1={f1_lr:.4f} (Thresh={best_thresh_lr:.2f})")

    # 4. TRAIN RANDOM FOREST
    print("\nTraining Random Forest Classifier (class_weight='balanced')...")
    rf_model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)

    val_probs_rf = rf_model.predict_proba(X_val)[:, 1]
    test_probs_rf = rf_model.predict_proba(X_test)[:, 1]

    # Tune threshold on Validation set to maximize F1 score
    best_thresh_rf = 0.5
    best_f1_rf = -1.0
    for t in np.linspace(0.05, 0.95, 91):
        f1_t = f1_score(y_val, (val_probs_rf >= t).astype(int), zero_division=0)
        if f1_t > best_f1_rf:
            best_f1_rf = f1_t
            best_thresh_rf = t

    test_preds_rf = (test_probs_rf >= best_thresh_rf).astype(int)
    roc_rf = float(roc_auc_score(y_test, test_probs_rf))
    p_prec_rf, p_rec_rf, _ = precision_recall_curve(y_test, test_probs_rf)
    pr_auc_rf = float(auc(p_rec_rf, p_prec_rf))
    prec_rf = float(precision_score(y_test, test_preds_rf, zero_division=0))
    rec_rf = float(recall_score(y_test, test_preds_rf, zero_division=0))
    f1_rf = float(f1_score(y_test, test_preds_rf, zero_division=0))
    cm_rf = confusion_matrix(y_test, test_preds_rf).tolist()

    print(f"Random Forest Test Metrics: ROC-AUC={roc_rf:.4f}, PR-AUC={pr_auc_rf:.4f}, F1={f1_rf:.4f} (Thresh={best_thresh_rf:.2f})")

    # 5. SERIALIZE ARTIFACTS
    with open(os.path.join(target_model_dir, 'logistic_regression.pkl'), 'wb') as f:
        pickle.dump(log_reg, f)
    with open(os.path.join(target_model_dir, 'random_forest.pkl'), 'wb') as f:
        pickle.dump(rf_model, f)
    with open(os.path.join(target_model_dir, 'scaler_supervised.pkl'), 'wb') as f:
        pickle.dump(scaler, f)

    sup_feature_schema = {
        "dataset_source": dataset_name,
        "tx_id_column": str(tx_id_col),
        "time_step_column": str(time_step_col),
        "active_feature_count": len(active_feature_cols),
        "active_feature_names": [str(c) for c in active_feature_cols]
    }
    with open(os.path.join(target_model_dir, 'supervised_feature_schema.json'), 'w') as f:
        json.dump(sup_feature_schema, f, indent=2)

    sup_metadata = {
        "dataset_name": dataset_name,
        "temporal_split": {
            "train": [1, 30],
            "validation": [31, 40],
            "test": [41, 49]
        },
        "samples": {
            "train_labeled": len(df_train),
            "validation_labeled": len(df_val),
            "test_labeled": len(df_test)
        },
        "thresholds_tuned_on_validation": {
            "logistic_regression": round(float(best_thresh_lr), 4),
            "random_forest": round(float(best_thresh_rf), 4)
        },
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(target_model_dir, 'supervised_training_metadata.json'), 'w') as f:
        json.dump(sup_metadata, f, indent=2)

    supervised_eval_report = {
        "dataset": dataset_name,
        "test_samples_evaluated": len(df_test),
        "illicit_test_samples": int(y_test.sum()),
        "licit_test_samples": int(len(y_test) - y_test.sum()),
        "logistic_regression": {
            "model_type": "Supervised Classification Baseline",
            "class_weight": "balanced",
            "roc_auc": round(roc_lr, 4),
            "pr_auc": round(pr_auc_lr, 4),
            "decision_threshold": round(float(best_thresh_lr), 4),
            "precision": round(prec_lr, 4),
            "recall": round(rec_lr, 4),
            "f1": round(f1_lr, 4),
            "confusion_matrix": cm_lr
        },
        "random_forest": {
            "model_type": "Supervised Non-Linear Ensemble Benchmark",
            "n_estimators": 100,
            "class_weight": "balanced",
            "roc_auc": round(roc_rf, 4),
            "pr_auc": round(pr_auc_rf, 4),
            "decision_threshold": round(float(best_thresh_rf), 4),
            "precision": round(prec_rf, 4),
            "recall": round(rec_rf, 4),
            "f1": round(f1_rf, 4),
            "confusion_matrix": cm_rf
        }
    }
    with open(os.path.join(target_model_dir, 'supervised_evaluation_report.json'), 'w') as f:
        json.dump(supervised_eval_report, f, indent=2)

    # LOAD EXISTING UNSUPERVISED METRICS FOR FINAL COMPARISON REPORT
    eval_unsupervised_file = os.path.join(target_model_dir, 'evaluation_report.json')
    eval_unsupervised = {}
    if os.path.exists(eval_unsupervised_file):
        with open(eval_unsupervised_file) as f:
            eval_unsupervised = json.load(f)

    iso_metrics = eval_unsupervised.get('isolation_forest', {})
    dbscan_metrics = eval_unsupervised.get('dbscan', {})

    final_comparison = {
        "dataset_name": dataset_name,
        "temporal_split": {"train": [1, 30], "validation": [31, 40], "test": [41, 49]},
        "test_labeled_samples": len(df_test),
        "unsupervised_anomaly_baseline": {
            "model": "Isolation Forest",
            "category": "Unsupervised Anomaly Detection",
            "roc_auc": iso_metrics.get('roc_auc', 0.0),
            "pr_auc": iso_metrics.get('pr_auc', 0.0),
            "precision": iso_metrics.get('precision', 0.0),
            "recall": iso_metrics.get('recall', 0.0),
            "f1": iso_metrics.get('f1', 0.0),
            "scientific_note": "Isolation Forest did not reliably rank illicit transactions above licit transactions on the held-out Elliptic++ test set under the current feature representation."
        },
        "supervised_classification_benchmarks": {
            "logistic_regression": {
                "model": "Logistic Regression",
                "category": "Supervised Linear Classification Benchmark",
                "roc_auc": round(roc_lr, 4),
                "pr_auc": round(pr_auc_lr, 4),
                "precision": round(prec_lr, 4),
                "recall": round(rec_lr, 4),
                "f1": round(f1_lr, 4),
                "decision_threshold": round(float(best_thresh_lr), 4)
            },
            "random_forest": {
                "model": "Random Forest",
                "category": "Supervised Non-Linear Ensemble Benchmark",
                "roc_auc": round(roc_rf, 4),
                "pr_auc": round(pr_auc_rf, 4),
                "precision": round(prec_rf, 4),
                "recall": round(rec_rf, 4),
                "f1": round(f1_rf, 4),
                "decision_threshold": round(float(best_thresh_rf), 4)
            }
        },
        "unsupervised_entity_clustering": {
            "model": "DBSCAN",
            "category": "Unsupervised Entity/Behavior Clustering Baseline",
            "eps": dbscan_metrics.get('eps', 2.0),
            "min_samples": dbscan_metrics.get('min_samples', 10),
            "clusters": dbscan_metrics.get('clusters', 0),
            "noise_ratio": dbscan_metrics.get('noise_ratio', 0.0),
            "silhouette": dbscan_metrics.get('silhouette', 0.0),
            "davies_bouldin": dbscan_metrics.get('davies_bouldin', 0.0),
            "calinski_harabasz": dbscan_metrics.get('calinski_harabasz', 0.0),
            "scientific_note": "DBSCAN identified candidate behavioral clusters, with cluster quality assessed using unsupervised validation metrics."
        },
        "terminology_standards": {
            "anomaly_signal": "Unsupervised Outlier Ranking Signal",
            "high_risk_flag": "High-risk investigative lead",
            "entity_cluster": "Candidate behavioral cluster"
        }
    }

    with open(os.path.join(target_model_dir, 'final_ml_comparison.json'), 'w') as f:
        json.dump(final_comparison, f, indent=2)

    print(f"✔ Supervised ML benchmark pipeline successfully completed for {dataset_name.upper()}!")

if __name__ == '__main__':
    run_supervised_pipeline('elliptic_v1', V1_DIR, is_v2=False)
    run_supervised_pipeline('elliptic_v2', V2_DIR, is_v2=True)
