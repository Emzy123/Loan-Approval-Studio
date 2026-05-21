"""Run inference with the trained loan approval model."""

import argparse
from pathlib import Path

import pandas as pd

from inference import (
    TARGET_COLUMN,
    artifacts_ready,
    default_sample,
    predict,
    strip_categoricals,
)
from inference import apply_encoders, load_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict loan approval from features.")
    parser.add_argument("--csv", type=Path, help="Optional CSV with feature columns")
    args = parser.parse_args()

    if not artifacts_ready():
        raise SystemExit("Missing model files. Run: python train.py")

    if args.csv:
        model, scaler, encoders, _ = load_artifacts()
        df = strip_categoricals(pd.read_csv(args.csv))
        y = df[TARGET_COLUMN] if TARGET_COLUMN in df.columns else None
        X = df.drop(columns=[TARGET_COLUMN], errors="ignore")
        X = apply_encoders(X, encoders)
        preds = model.predict(scaler.transform(X))
        for i, pred in enumerate(preds):
            label = "Approved" if int(pred) == 1 else "Rejected"
            actual = ""
            if y is not None:
                actual = f" (actual: {y.iloc[i]})"
            print(f"row {i}: {label}{actual}")
        return

    sample = default_sample()
    label, confidence, probs = predict(sample)
    print(f"Prediction: {label} ({confidence:.1%} confidence)")
    for name, p in probs.items():
        print(f"  {name}: {p:.1%}")


if __name__ == "__main__":
    main()
