"""Build Shino training CSV from Lending Club accepted/rejected application files."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "lending_club" / "raw"
ACCEPTED_PATH = RAW_DIR / "accepted_2007_to_2018Q4.csv.gz"
REJECTED_PATH = RAW_DIR / "rejected_2007_to_2018Q4.csv.gz"
OUTPUT_PATH = ROOT / "data" / "lending_club" / "loan_applications.csv"

USD_TO_INR = 83.0
TARGET_COLUMN = "loan_status"

ACADEMIC_TITLE_PATTERN = (
    r"professor|teacher|lecturer|faculty|research|scientist|instructor|"
    r"dean|academic|physician|doctor|nurse|engineer|architect|analyst"
)

ACCEPTED_USECOLS = [
    "loan_amnt",
    "term",
    "emp_title",
    "annual_inc",
    "verification_status",
    "fico_range_low",
    "fico_range_high",
    "home_ownership",
    "revol_bal",
]

REJECTED_USECOLS = [
    "Amount Requested",
    "Risk_Score",
    "Debt-To-Income Ratio",
    "Employment Length",
]


def _parse_dti(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.replace("%", "", regex=False)
        .replace({"": np.nan, "nan": np.nan})
        .astype(float)
        .clip(lower=0.5)
        .fillna(20.0)
    )


def _employment_from_length(series: pd.Series) -> pd.Series:
    senior = series.astype(str).str.strip().str.lower().isin(
        {"10+ years", "9 years", "8 years", "7 years"}
    )
    return np.where(senior, "Academic Staff", "Non Academic Staff")


def _asset_columns(income_inr: pd.Series, home_ownership: pd.Series, revol_bal_inr: pd.Series) -> pd.DataFrame:
    ho = home_ownership.fillna("").str.upper()
    residential = np.where(
        ho.isin(["MORTGAGE", "OWN"]),
        (income_inr * 0.6).round(),
        (income_inr * 0.15).round(),
    ).astype(int)
    commercial = (income_inr * 0.05).round().astype(int)
    luxury = (income_inr * 0.08).round().astype(int)
    bank = np.maximum((income_inr * 0.25).round().astype(int) - revol_bal_inr.fillna(0).astype(int), 0)
    return pd.DataFrame(
        {
            "residential_assets_value": residential,
            "commercial_assets_value": commercial,
            "luxury_assets_value": luxury,
            "bank_asset_value": bank,
        }
    )


def transform_accepted(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["loan_amnt", "annual_inc", "fico_range_low", "fico_range_high"])
    df = df[(df["loan_amnt"] > 0) & (df["annual_inc"] > 0)]

    income_inr = (df["annual_inc"] * USD_TO_INR).round().astype(int)
    loan_inr = (df["loan_amnt"] * USD_TO_INR).round().astype(int)
    term = df["term"].astype(str).str.extract(r"(\d+)", expand=False).fillna("36").astype(int)
    cibil = ((df["fico_range_low"] + df["fico_range_high"]) / 2).round().astype(int)

    education = np.where(
        df["verification_status"].isin(["Verified", "Source Verified"]),
        "Graduate",
        "Not Graduate",
    )
    is_academic = df["emp_title"].fillna("").str.lower().str.contains(
        ACADEMIC_TITLE_PATTERN, regex=True, na=False
    )
    employment = np.where(is_academic, "Academic Staff", "Non Academic Staff")
    revol_inr = (df["revol_bal"].fillna(0) * USD_TO_INR).round().astype(int)
    assets = _asset_columns(income_inr, df["home_ownership"], revol_inr)

    return pd.DataFrame(
        {
            "no_of_dependents": 0,
            "education": education,
            "self_employed": employment,
            "income_annum": income_inr,
            "loan_amount": loan_inr,
            "loan_term": term,
            "cibil_score": cibil,
            **assets,
            TARGET_COLUMN: "Approved",
        }
    )


def transform_rejected(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["Amount Requested", "Risk_Score"])
    df = df[df["Amount Requested"] > 0]

    dti = _parse_dti(df["Debt-To-Income Ratio"])
    amount_usd = df["Amount Requested"].astype(float)
    term = pd.Series(36, index=df.index)
    monthly_debt = amount_usd / term
    annual_usd = (monthly_debt / (dti / 100.0)) * 12.0

    income_inr = (annual_usd * USD_TO_INR).round().astype(int)
    loan_inr = (amount_usd * USD_TO_INR).round().astype(int)
    cibil = df["Risk_Score"].round().astype(int)
    education = np.where(cibil >= 680, "Graduate", "Not Graduate")
    employment = _employment_from_length(df["Employment Length"])
    assets = _asset_columns(income_inr, pd.Series("", index=df.index), pd.Series(0, index=df.index))

    return pd.DataFrame(
        {
            "no_of_dependents": 0,
            "education": education,
            "self_employed": employment,
            "income_annum": income_inr,
            "loan_amount": loan_inr,
            "loan_term": term,
            "cibil_score": cibil,
            **assets,
            TARGET_COLUMN: "Rejected",
        }
    )


def _random_sample_file(
    path: Path,
    n: int,
    transform,
    usecols: list[str],
    random_state: int,
    keep_prob: float,
    low_memory: bool = True,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    current_keep = keep_prob

    while current_keep <= 0.2:
        def skip_row(row_index: int, keep: float = current_keep) -> bool:
            return row_index > 0 and rng.random() > keep

        raw = pd.read_csv(
            path,
            usecols=usecols,
            skiprows=skip_row,
            low_memory=low_memory,
        )
        transformed = transform(raw)
        if len(transformed) >= n:
            return transformed.sample(n=n, random_state=random_state).reset_index(drop=True)
        if len(transformed) == 0:
            raise ValueError(f"No usable rows after transforming {path.name}")
        current_keep *= 2
        rng = np.random.default_rng(random_state)

    return transformed.reset_index(drop=True)


def build_dataset(
    accepted_n: int = 25_000,
    rejected_n: int = 25_000,
    random_state: int = 42,
    accepted_keep_prob: float = 0.02,
    rejected_keep_prob: float = 0.001,
) -> pd.DataFrame:
    if not ACCEPTED_PATH.exists():
        raise FileNotFoundError(f"Missing accepted file: {ACCEPTED_PATH}")
    if not REJECTED_PATH.exists():
        raise FileNotFoundError(f"Missing rejected file: {REJECTED_PATH}")

    print(f"Sampling up to {accepted_n:,} approved applications from {ACCEPTED_PATH.name}…")
    approved = _random_sample_file(
        ACCEPTED_PATH,
        accepted_n,
        transform_accepted,
        ACCEPTED_USECOLS,
        random_state,
        accepted_keep_prob,
        low_memory=True,
    )
    print(f"  collected {len(approved):,} approved rows")

    print(f"Sampling up to {rejected_n:,} rejected applications from {REJECTED_PATH.name}…")
    rejected = _random_sample_file(
        REJECTED_PATH,
        rejected_n,
        transform_rejected,
        REJECTED_USECOLS,
        random_state + 1,
        rejected_keep_prob,
        low_memory=False,
    )
    print(f"  collected {len(rejected):,} rejected rows")

    combined = pd.concat([approved, rejected], ignore_index=True)
    combined = combined.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Lending Club data for Shino training.")
    parser.add_argument("--accepted", type=int, default=25_000, help="Approved sample size")
    parser.add_argument("--rejected", type=int, default=25_000, help="Rejected sample size")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = build_dataset(args.accepted, args.rejected, random_state=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"\nWrote {len(df):,} rows to {args.output}")
    print(df[TARGET_COLUMN].value_counts())
    print(df.head())


if __name__ == "__main__":
    main()
