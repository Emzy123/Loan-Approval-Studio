"""Currency definitions and conversion (model trained on INR amounts)."""

from __future__ import annotations

MONEY_FIELDS = [
    "income_annum",
    "loan_amount",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]

# amount_inr = amount_foreign * rate_to_inr
CURRENCIES: dict[str, dict[str, str | float]] = {
    "INR": {"name": "Indian Rupee", "symbol": "₹", "flag": "🇮🇳", "rate_to_inr": 1.0},
    "USD": {"name": "US Dollar", "symbol": "$", "flag": "🇺🇸", "rate_to_inr": 83.0},
    "EUR": {"name": "Euro", "symbol": "€", "flag": "🇪🇺", "rate_to_inr": 90.0},
    "GBP": {"name": "British Pound", "symbol": "£", "flag": "🇬🇧", "rate_to_inr": 105.0},
    "NGN": {"name": "Nigerian Naira", "symbol": "₦", "flag": "🇳🇬", "rate_to_inr": 0.055},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "flag": "🇨🇦", "rate_to_inr": 61.0},
    "AUD": {"name": "Australian Dollar", "symbol": "A$", "flag": "🇦🇺", "rate_to_inr": 54.0},
    "JPY": {"name": "Japanese Yen", "symbol": "¥", "flag": "🇯🇵", "rate_to_inr": 0.55},
    "CHF": {"name": "Swiss Franc", "symbol": "Fr", "flag": "🇨🇭", "rate_to_inr": 95.0},
    "ZAR": {"name": "South African Rand", "symbol": "R", "flag": "🇿🇦", "rate_to_inr": 4.5},
}

DEFAULT_CURRENCY = "INR"


def currency_codes() -> list[str]:
    return list(CURRENCIES.keys())


def currency_label(code: str) -> str:
    c = CURRENCIES[code]
    return f"{c['flag']} {code} — {c['name']}"


def to_inr(amount: float, code: str) -> int:
    rate = float(CURRENCIES[code]["rate_to_inr"])
    return int(round(amount * rate))


def from_inr(amount_inr: float, code: str) -> int:
    rate = float(CURRENCIES[code]["rate_to_inr"])
    return int(round(amount_inr / rate))


def convert_form_money(form: dict, from_code: str, to_code: str) -> dict:
    if from_code == to_code:
        return form
    out = dict(form)
    for field in MONEY_FIELDS:
        inr = to_inr(out[field], from_code)
        out[field] = from_inr(inr, to_code)
    return out


def format_money(value: int | float, code: str) -> str:
    n = float(value)
    sym = str(CURRENCIES[code]["symbol"])
    if code == "INR":
        if n >= 10_000_000:
            return f"{sym}{n / 10_000_000:.2f} Cr"
        if n >= 100_000:
            return f"{sym}{n / 100_000:.2f} L"
        return f"{sym}{n:,.0f}"
    if n >= 1_000_000_000:
        return f"{sym}{n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{sym}{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{sym}{n / 1_000:.1f}K"
    return f"{sym}{n:,.0f}"


def input_step(code: str) -> int:
    if code == "INR":
        return 100_000
    if code in ("USD", "EUR", "GBP", "CAD", "AUD", "CHF"):
        return 1_000
    if code == "NGN":
        return 50_000
    if code == "JPY":
        return 10_000
    return 1_000


def sample_for_model(form: dict, code: str) -> dict:
    """Convert monetary fields to INR for the trained model."""
    out = dict(form)
    for field in MONEY_FIELDS:
        out[field] = to_inr(out[field], code)
    return out
