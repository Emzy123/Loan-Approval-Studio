"""Load artifacts and run loan approval inference."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "loan_model.pkl"
SCALER_PATH = ROOT / "scaler.pkl"
ENCODERS_PATH = ROOT / "encoders.pkl"
METADATA_PATH = ROOT / "model_metadata.pkl"

FEATURE_COLUMNS = [
    "no_of_dependents",
    "education",
    "self_employed",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]

CATEGORICAL_COLUMNS = ["education", "self_employed"]
TARGET_COLUMN = "loan_status"


def _categorical_columns(df: pd.DataFrame) -> pd.Index:
    return df.select_dtypes(include=["object", "str"]).columns


def strip_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in _categorical_columns(out):
        out[col] = out[col].astype(str).str.strip()
    return out


def fit_encoders(df: pd.DataFrame) -> dict[str, LabelEncoder]:
    encoders: dict[str, LabelEncoder] = {}
    for col in _categorical_columns(df):
        if col == TARGET_COLUMN:
            continue
        le = LabelEncoder()
        le.fit(df[col])
        encoders[col] = le
    return encoders


def apply_encoders(df: pd.DataFrame, encoders: dict[str, LabelEncoder]) -> pd.DataFrame:
    out = df.copy()
    for col, le in encoders.items():
        out[col] = le.transform(out[col])
    return out


def artifacts_ready() -> bool:
    return MODEL_PATH.exists() and SCALER_PATH.exists() and ENCODERS_PATH.exists()


def load_artifacts() -> tuple[object, StandardScaler, dict[str, LabelEncoder], dict]:
    if not artifacts_ready():
        raise FileNotFoundError(
            "Missing model files. Run: python train.py"
        )
    model = joblib.load(MODEL_PATH)
    scaler: StandardScaler = joblib.load(SCALER_PATH)
    encoders: dict[str, LabelEncoder] = joblib.load(ENCODERS_PATH)
    metadata: dict = joblib.load(METADATA_PATH) if METADATA_PATH.exists() else {}
    return model, scaler, encoders, metadata


def prepare_features(sample: dict, encoders: dict[str, LabelEncoder]) -> pd.DataFrame:
    row = pd.DataFrame([sample])
    row = strip_categoricals(row)
    encoded = apply_encoders(row, encoders)
    return encoded[FEATURE_COLUMNS]


def predict(sample: dict) -> tuple[str, float, dict[str, float]]:
    model, scaler, encoders, metadata = load_artifacts()
    features = prepare_features(sample, encoders)
    scaled = scaler.transform(features)
    pred = int(model.predict(scaled)[0])
    proba = model.predict_proba(scaled)[0]
    classes = list(getattr(model, "classes_", [0, 1]))
    prob_map = {
        _class_label(int(c)): float(p) for c, p in zip(classes, proba)
    }
    label = _class_label(pred)
    confidence = prob_map.get(label, float(max(proba)))
    return label, confidence, prob_map


def _class_label(code: int) -> str:
    return "Approved" if code == 1 else "Rejected"


def category_options(encoders: dict[str, LabelEncoder]) -> dict[str, list[str]]:
    return {col: list(le.classes_) for col, le in encoders.items()}


def default_sample() -> dict:
    return {
        "no_of_dependents": 2,
        "education": "Graduate",
        "self_employed": "No",
        "income_annum": 9_600_000,
        "loan_amount": 29_900_000,
        "loan_term": 12,
        "cibil_score": 778,
        "residential_assets_value": 2_400_000,
        "commercial_assets_value": 17_600_000,
        "luxury_assets_value": 22_700_000,
        "bank_asset_value": 8_000_000,
    }
