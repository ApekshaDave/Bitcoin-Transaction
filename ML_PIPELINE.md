# SIH26146 — Production ML Pipeline & Scientific Diagnostic Architecture

## Executive Summary
This document details the scientific validation and diagnostic architecture of the **SIH26146 Bitcoin Transaction Traffic & Network Monitoring Platform**. Operating 100% offline, the platform provides reproducible, unmanipulated machine learning evaluation on the **Elliptic v1** and **Elliptic v2 (Elliptic++)** benchmark datasets.

---

## 1. Feature-Count Terminology & Schema Verification

| Dataset Scope | Total File Columns | Identifier Columns Excluded | Final Numerical Feature Count ($X_{\text{transaction}}$) |
| :--- | :--- | :--- | :--- |
| **Elliptic v1** | 167 columns | `col_0` (`txId`), `col_1` (`time_step`) | **165** features |
| **Elliptic v2 (Elliptic++)** | 184 columns | `txId`, `Time step` | **182** features |

- **Label Isolation**: Ground-truth class labels (`class` column) are strictly excluded from all training feature matrices.
- **Identifier Isolation**: Primary identifiers (`txId`, `address`, `time_step`) are excluded from model training features.

---

## 2. Actor / Wallet Layer Semantics
- **`wallets_features.csv`**: Contains **1,268,260 feature rows** across 56 numerical wallet features.
- **`wallets_classes.csv`**: Contains **822,942 class records** (`address`, `class`).
  - **Class 1 (Illicit)**: 14,266
  - **Class 2 (Licit)**: 251,088
  - **Class 3 (Unknown)**: 557,588
- **Semantics**: `wallets_features.csv` contains temporal actor records representing wallet behavioral snapshots across time steps.

---

## 3. Chronological Temporal Data Split
Transactions are split chronologically by `Time step` to prevent temporal data leakage:
- **TRAIN Set**: Time Steps **1 to 30** (123,287 transactions)
- **VALIDATION Set**: Time Steps **31 to 40** (38,316 transactions)
- **TEST Set**: Time Steps **41 to 49** (42,166 total transactions; **9,973 labeled test transactions** evaluated)

`StandardScaler` preprocessing is fitted **strictly** on the TRAIN set and applied to VALIDATION and TEST sets.

---

## 4. Isolation Forest Score Diagnostics & Orientation

### Mathematical Transformation Pipeline
1. **Raw Decision Function**: `raw_score = iso_forest.decision_function(X)` (Higher = More Normal, Lower = More Anomalous).
2. **Score Inversion**: `anomaly_raw = -raw_score` (Higher = More Anomalous).
3. **MinMax Normalization**: `anomaly_score = clip((-raw_score - min_train) / (max_train - min_train), 0.0, 1.0)`.

### Test Set Score Distributions (Held-Out Test Steps 41-49)

| Statistic | Class 1 (Illicit) | Class 2 (Licit) |
| :--- | :--- | :--- |
| **Count** | 524 | 9,449 |
| **Mean** | `0.1672` | `0.2954` |
| **Std Dev** | `0.0916` | `0.1639` |
| **Min** | `0.0551` | `0.0463` |
| **25th Percentile** | `0.0936` | `0.1775` |
| **Median (p50)** | **`0.1259`** | **`0.2643`** |
| **75th Percentile** | `0.2431` | `0.3744` |
| **Max** | `0.4130` | `1.0000` |

### Scientific Finding
Unsupervised tree partitioners (Isolation Forest) rank illicit Bitcoin transactions with lower anomaly scores (**median 0.1259**) than licit transactions (**median 0.2643**). On Bitcoin's public ledger, illicit entities (ransomware, darknet services, mixing pools) execute highly standardized, repetitive graph transactions that form dense behavioral clusters in feature space. In contrast, licit transactions contain extreme volume and fee outliers (extending to **1.0000**), causing raw unsupervised anomaly detectors to yield **0.2439 ROC-AUC** without supervised fine-tuning.

---

## 5. Controlled Feature Group Experiments

| Experiment | Feature Subset | Feature Count | Held-Out Test ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :--- | :--- |
| **Exp A** | All Features | 182 | **`0.2439`** | **`0.0316`** |
| **Exp B** | Local Features Only | 93 | **`0.2312`** | **`0.0298`** |
| **Exp C** | Aggregate Features Only | 89 | **`0.2640`** | **`0.0345`** |

---

## 6. DBSCAN & PCA Representation Tuning

| Representation | PCA Components | Variance Explained | `eps` | `min_samples` | Clusters | Noise % | Silhouette | Calinski-Harabasz | Davies-Bouldin |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Baseline** | None (182) | 100% | 2.0 | 10 | 7 | 93.9% | -0.3406 | 5.01 | 2.55 |
| **PCA Subspace** | 5 | 53.0% | 0.8 | 10 | **12** | **56.5%** | **-0.2698** | **362.5** | **1.69** |
| **PCA Subspace** | 10 | 66.8% | 1.0 | 10 | 9 | 64.2% | -0.2810 | 184.2 | 1.95 |

PCA dimensionality reduction (5 components) significantly improves behavioral cluster formation, reducing noise ratio to **56.5%** and raising Calinski-Harabasz index to **362.5**.

---

## 7. Multi-Factor Composite Risk Formula

$$R = 100 \times \left(0.25 \cdot S_{\text{anomaly}} + 0.25 \cdot S_{\text{peeling}} + 0.20 \cdot S_{\text{mixing}} + 0.15 \cdot S_{\text{network}} + 0.15 \cdot S_{\text{graph}}\right)$$

Where $S_i \in [0.0, 1.0]$ and weights sum to $1.0$.

---

## 8. Saved Artifacts & Diagnostic Files
- `models/elliptic_v1/` & `models/elliptic_v2/`:
  - `isolation_forest.pkl`
  - `logistic_regression.pkl`
  - `random_forest.pkl`
  - `scaler.pkl`
  - `scaler_supervised.pkl`
  - `dbscan.pkl`
  - `feature_schema.json`
  - `supervised_feature_schema.json`
  - `training_metadata.json`
  - `supervised_training_metadata.json`
  - `evaluation_report.json`
  - `supervised_evaluation_report.json`
  - `ml_diagnostic_report.json`
  - `final_ml_comparison.json`

---

## 9. Supervised ML Benchmark & Final Model Comparison

To complement the unsupervised anomaly detection baseline, supervised classification models were trained on labeled transactions (**Class 1 Illicit** vs **Class 2 Licit**) with **Class 3 (Unknown) strictly excluded** from supervised training and evaluation.

### Supervised Training Setup
- **Chronological Temporal Split**: Train (Steps 1–30, 26,905 labeled txs), Validation (Steps 31–40, 7,411 labeled txs), Test (Steps 41–49, 9,973 held-out labeled txs).
- **Class Imbalance Handling**: `class_weight='balanced'`.
- **Threshold Tuning**: Decision thresholds tuned on the Validation set (Steps 31–40) to maximize Validation F1 score and applied **once** to the held-out Test set (Steps 41–49).

### Final Benchmark Performance Comparison (Elliptic++ Held-Out Test Set, $N=9,973$)

| Model Category | Algorithm | Model Type | Held-Out Test ROC-AUC | PR-AUC | Precision (Illicit) | Recall (Illicit) | F1 Score | Decision Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Unsupervised Anomaly** | **Isolation Forest** | Outlier Ranking Baseline | `0.2439` | `0.0316` | 1.2% | 7.8% | `0.0210` | N/A |
| **Supervised Linear** | **Logistic Regression** | Linear Classification | `0.7812` | `0.4852` | 58.4% | 55.2% | `0.5673` | `0.46` (Val tuned) |
| **Supervised Non-Linear** | **Random Forest** | Non-Linear Ensemble | **`0.8343`** | **`0.6357`** | **93.6%** | **55.3%** | **`0.6954`** | `0.42` (Val tuned) |

### Key Scientific Findings
1. **Unsupervised vs Supervised Mechanics**:
   - *Isolation Forest did not reliably rank illicit transactions above licit transactions on the held-out Elliptic++ test set under the current feature representation.* Raw feature space volume outliers do not correlate with illicit transaction patterns.
   - *Random Forest non-linear decision boundaries achieve high illicit transaction precision (93.6%) and strong PR-AUC (`0.6357`).*
2. **DBSCAN Behavioral Clustering**:
   - *DBSCAN identified candidate behavioral clusters, with cluster quality assessed using unsupervised validation metrics.* (Raw: 7 clusters, 93.9% noise, Silhouette `-0.3406`; PCA-5: 12 clusters, 56.5% noise, Silhouette `-0.2698`, Calinski-Harabasz `362.5`).
3. **Scientific Terminology Standards**:
   - Isolation Forest output: **Unsupervised Outlier Ranking Signal**.
   - Composite Risk score $\ge 75$: **High-risk investigative lead**.
   - DBSCAN output: **Candidate behavioral cluster**.

