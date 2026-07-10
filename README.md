# Shino · Loan Approval Studio

A machine learning system for loan approval prediction with an interactive web UI. Train classifiers on loan application data, evaluate performance, and run predictions through a guided multi-step interface.

## Features

- **Multiple ML Models**: Logistic Regression, Decision Tree, Random Forest, and SVM classifiers
- **Best Model Selection**: Automatically selects the model with highest test accuracy
- **Interactive Web UI**: 5-step guided flow (Currency → Profile → Financials → Review → Decision)
- **Multi-Currency Support**: Input values in various currencies with automatic conversion to INR
- **Performance Metrics**: Confusion matrix, ROC curve, precision-recall curve, and feature importance
- **CLI Predictions**: Command-line interface for batch predictions
- **Lending Club Data**: Support for preparing training data from Lending Club accepted/rejected applications

## Setup

```bash
cd /home/purist/Desktop/projects/shino
python3 -m venv .venv
source .venv/bin/activate
pip install --default-timeout=300 --retries 10 -r requirements.txt
```

If downloads time out, use the helper script (same flags, core deps only):

```bash
chmod +x install.sh
./install.sh
```

For Jupyter notebooks, install extras after core deps succeed:

```bash
pip install --default-timeout=300 --retries 10 -r requirements-notebook.txt
```

## Data Preparation

The project supports two datasets:

1. **Legacy Dataset**: `loan_approval_dataset_cleaned.csv` (included)
2. **Lending Club Dataset**: Built from raw Lending Club accepted/rejected files

To prepare the Lending Club dataset (requires raw files in `data/lending_club/raw/`):

```bash
python prepare_lending_club.py
```

This creates `data/lending_club/loan_applications.csv` with transformed features matching the model schema.

## Training

Train on the default Lending Club dataset (auto-prepares if missing):

```bash
python train.py --prepare
```

Train on the legacy dataset:

```bash
python train.py --legacy
```

Train on a custom dataset:

```bash
python train.py --dataset /path/to/your/data.csv
```

Training outputs:

- `loan_model.pkl` — best model (by test accuracy)
- `scaler.pkl` — fitted `StandardScaler`
- `encoders.pkl` — fitted label encoders for categorical features
- `model_metadata.pkl` — model metadata (name, features, dataset info)
- `confusion_matrix.png`, `roc_curve.png`, `precision_recall_curve.png`, `feature_importance.png`

## Predictions

```bash
python predict.py
```

Predict from a CSV (feature columns only, or includes `loan_status`):

```bash
python predict.py --csv loan_approval_dataset_cleaned.csv
```

## Web UI

Install UI dependencies (after core `requirements.txt`):

```bash
pip install --default-timeout=600 --retries 15 -r requirements-ui.txt
```

Retrain to ensure encoders are saved (required for the UI):

```bash
python train.py --prepare
```

Start the app:

```bash
streamlit run app.py
# or
./run_ui.sh
```
Open the URL shown in the terminal (usually http://localhost:8501).

The UI uses a **5-step guided flow**:
1. **Currency Selection** — Choose your preferred currency for inputs
2. **Applicant Profile** — Dependents, education, employment type, CIBIL score, loan term
3. **Financial Position** — Income, loan amount, and asset values
4. **Review** — Confirm all details before prediction
5. **Credit Decision** — View approval/rejection verdict with confidence breakdown

## Jupyter Notebooks

Open `loan_training.ipynb` and run all cells. It uses the same logic as `train.py`.

The older `loan_model.ipynb` is kept for reference; use `loan_training.ipynb` for this dataset.


## Dataset Schema

Target column: `loan_status` (`Approved` / `Rejected`)

Feature columns:
- `no_of_dependents` — Number of financial dependents
- `education` — Education level (`Graduate` / `Not Graduate`)
- `self_employed` — Employment type (`Academic Staff` / `Non Academic Staff`)
- `income_annum` — Annual income (INR)
- `loan_amount` — Requested loan amount (INR)
- `loan_term` — Loan term in months
- `cibil_score` — Credit bureau score (300-900)
- `residential_assets_value` — Value of residential assets (INR)
- `commercial_assets_value` — Value of commercial assets (INR)
- `luxury_assets_value` — Value of luxury assets (INR)
- `bank_asset_value` — Value of bank assets (INR)
