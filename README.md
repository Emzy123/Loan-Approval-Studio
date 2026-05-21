# Loan Approval ML

Train and evaluate classifiers on loan application data, then run predictions.

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

## Train (recommended)

```bash
python train.py
```

Writes:

- `loan_model.pkl` — best model (by test accuracy)
- `scaler.pkl` — fitted `StandardScaler`
- `confusion_matrix.png`, `roc_curve.png`, `precision_recall_curve.png`

## Predict

After training:

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

Retrain so encoders are saved (required for the UI):

```bash
python train.py
```

Start the app:

```bash
streamlit run app.py
# or
./run_ui.sh
```

Open the URL shown in the terminal (usually http://localhost:8501).

The UI uses a **4-step guided flow**: Profile → Financials → Review → Decision, with branded styling and confidence breakdown.

## Jupyter notebook

Open `loan_training.ipynb` and run all cells. It uses the same logic as `train.py`.

The older `loan_model.ipynb` is kept for reference; use `loan_training.ipynb` for this dataset.

## Dataset

`loan_approval_dataset_cleaned.csv` — target column: `loan_status` (`Approved` / `Rejected`).
