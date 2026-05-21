"""Streamlit UI — guided loan approval experience."""

from pathlib import Path

import streamlit as st

from inference import (
    artifacts_ready,
    category_options,
    default_sample,
    load_artifacts,
    predict,
)
from ui.components import (
    STEPS,
    cibil_hint,
    render_hero,
    render_review_table,
    render_sidebar_brand,
    render_sidebar_currency,
    render_stepper,
    render_verdict,
    section_header,
)
from ui.currencies import (
    CURRENCIES,
    DEFAULT_CURRENCY,
    MONEY_FIELDS,
    convert_form_money,
    currency_codes,
    currency_label,
    format_money,
    input_step,
    sample_for_model,
)
from ui.styles import inject_styles

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Shino · Loan Approval Studio",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _init_state() -> None:
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "currency" not in st.session_state:
        st.session_state.currency = DEFAULT_CURRENCY
    if "form" not in st.session_state:
        st.session_state.form = default_sample()
    if "result" not in st.session_state:
        st.session_state.result = None


def _save(**kwargs) -> None:
    st.session_state.form.update(kwargs)


def _reset_application() -> None:
    st.session_state.step = 0
    st.session_state.currency = DEFAULT_CURRENCY
    st.session_state.form = default_sample()
    st.session_state.result = None


@st.cache_resource
def _load():
    return load_artifacts()


def _field_labels() -> dict[str, str]:
    return {
        "no_of_dependents": "Dependents",
        "education": "Education",
        "self_employed": "Self employed",
        "income_annum": "Annual income",
        "loan_amount": "Loan amount",
        "loan_term": "Loan term",
        "cibil_score": "CIBIL score",
        "residential_assets_value": "Residential assets",
        "commercial_assets_value": "Commercial assets",
        "luxury_assets_value": "Luxury assets",
        "bank_asset_value": "Bank assets",
    }


def _review_rows(sample: dict, currency: str) -> list[tuple[str, str]]:
    labels = _field_labels()
    rows = []
    for key, label in labels.items():
        val = sample[key]
        if key in MONEY_FIELDS:
            display = format_money(val, currency)
        elif key == "loan_term":
            display = f"{val} months"
        else:
            display = str(val)
        rows.append((label, display))
    return rows


def step_currency() -> None:
    with st.container(border=True):
        section_header(
            "Choose your currency",
            "All income and asset amounts will be entered in this currency. "
            "Exchange rates are indicative; the credit model normalizes to INR.",
        )
        codes = currency_codes()
        prev = st.session_state.currency
        idx = codes.index(prev) if prev in codes else 0

        selected = st.selectbox(
            "Application currency",
            codes,
            index=idx,
            format_func=currency_label,
            help="Pick the currency you use for income, loan, and assets.",
        )

        popular = st.columns(4)
        for col, code in zip(popular, ("USD", "EUR", "GBP", "NGN")):
            c = CURRENCIES[code]
            with col:
                st.markdown(f"**{c['flag']} {code}** — {c['symbol']}")

        st.info(
            f"Selected: **{currency_label(selected)}**. "
            f"Example formatting: {format_money(2_500_000, selected)}."
        )

    if selected != prev:
        st.session_state.form = convert_form_money(st.session_state.form, prev, selected)
    st.session_state.currency = selected


def step_profile(options: dict, defaults: dict) -> None:
    with st.container(border=True):
        section_header("Applicant profile", "Tell us about the borrower and credit health.")
        c1, c2 = st.columns(2)
        with c1:
            deps = st.number_input(
                "Number of dependents",
                min_value=0,
                max_value=10,
                value=int(defaults["no_of_dependents"]),
                help="Financial dependents supported by the applicant.",
            )
            edu = st.selectbox(
                "Education",
                options["education"],
                index=options["education"].index(defaults["education"])
                if defaults["education"] in options["education"]
                else 0,
            )
            emp = st.selectbox(
                "Employment type",
                options["self_employed"],
                index=options["self_employed"].index(defaults["self_employed"])
                if defaults["self_employed"] in options["self_employed"]
                else 0,
                help="Whether the applicant is self-employed.",
            )
        with c2:
            cibil = st.slider(
                "CIBIL score",
                min_value=300,
                max_value=900,
                value=int(defaults["cibil_score"]),
                help="Credit bureau score used as a primary risk signal.",
            )
            st.caption(cibil_hint(cibil))
            term = st.number_input(
                "Loan term (months)",
                min_value=1,
                max_value=360,
                value=int(defaults["loan_term"]),
            )
    _save(
        no_of_dependents=deps,
        education=edu,
        self_employed=emp,
        cibil_score=cibil,
        loan_term=term,
    )


def step_financials(defaults: dict, currency: str) -> None:
    sym = str(CURRENCIES[currency]["symbol"])
    step = input_step(currency)

    with st.container(border=True):
        section_header(
            "Financial position",
            f"Income, requested loan, and declared asset values ({currency}).",
        )
        c1, c2 = st.columns(2)
        with c1:
            income = st.number_input(
                f"Annual income ({sym})",
                min_value=0,
                value=int(defaults["income_annum"]),
                step=step,
                format="%d",
            )
            st.caption(format_money(income, currency))
            loan = st.number_input(
                f"Requested loan ({sym})",
                min_value=0,
                value=int(defaults["loan_amount"]),
                step=step,
                format="%d",
            )
            st.caption(format_money(loan, currency))
            if income > 0:
                ratio = loan / income
                st.markdown(
                    f'<span class="metric-pill">Loan-to-income: {ratio:.1f}×</span>',
                    unsafe_allow_html=True,
                )
        with c2:
            res = st.number_input(
                f"Residential assets ({sym})",
                0,
                value=int(defaults["residential_assets_value"]),
                step=step,
                format="%d",
            )
            com = st.number_input(
                f"Commercial assets ({sym})",
                0,
                value=int(defaults["commercial_assets_value"]),
                step=step,
                format="%d",
            )
            lux = st.number_input(
                f"Luxury assets ({sym})",
                0,
                value=int(defaults["luxury_assets_value"]),
                step=step,
                format="%d",
            )
            bank = st.number_input(
                f"Bank assets ({sym})",
                0,
                value=int(defaults["bank_asset_value"]),
                step=step,
                format="%d",
            )
        total_assets = res + com + lux + bank
        st.markdown(
            f'<span class="metric-pill">Total declared assets: '
            f"{format_money(total_assets, currency)}</span>",
            unsafe_allow_html=True,
        )
    _save(
        income_annum=income,
        loan_amount=loan,
        residential_assets_value=res,
        commercial_assets_value=com,
        luxury_assets_value=lux,
        bank_asset_value=bank,
    )


def step_review(sample: dict, currency: str) -> None:
    section_header("Review application", "Confirm details before running the credit model.")
    render_review_table(_review_rows(sample, currency))


def step_decision(sample: dict, model_name: str, currency: str) -> None:
    with st.container(border=True):
        section_header("Credit decision", f"Powered by {model_name}")
        if st.session_state.result is None:
            with st.spinner("Analyzing application…"):
                model_sample = sample_for_model(sample, currency)
                label, confidence, probs = predict(model_sample)
                st.session_state.result = (label, confidence, probs)
        label, confidence, probs = st.session_state.result
        render_verdict(label, confidence, probs)
        st.caption(
            f"Monetary inputs converted from {currency} to INR using indicative "
            f"exchange rates before scoring."
        )


def main() -> None:
    inject_styles()
    _init_state()

    if not artifacts_ready():
        render_hero()
        st.error("Model artifacts missing")
        st.markdown("Train the model once, then refresh this page.")
        st.code(
            "cd ~/Desktop/projects/shino\n"
            "source .venv/bin/activate\n"
            "python train.py\n"
            "streamlit run app.py",
            language="bash",
        )
        st.stop()

    model, _, encoders, metadata = _load()
    options = category_options(encoders)
    defaults = st.session_state.form
    currency = st.session_state.currency
    model_name = metadata.get("best_model_name", type(model).__name__)
    chart = ROOT / "feature_importance.png"

    with st.sidebar:
        render_sidebar_brand(model_name, chart.exists(), str(chart) if chart.exists() else None)
        st.divider()
        render_sidebar_currency(currency)
        st.divider()
        if st.button("↺ Reset application", use_container_width=True):
            _reset_application()
            st.rerun()

    render_hero()
    render_stepper(st.session_state.step)

    step = st.session_state.step
    sample = st.session_state.form
    last_step = len(STEPS) - 1

    if step == 0:
        step_currency()
    elif step == 1:
        step_profile(options, defaults)
    elif step == 2:
        step_financials(defaults, currency)
    elif step == 3:
        step_review(sample, currency)
    elif step == 4:
        step_decision(sample, model_name, currency)

    st.markdown("<br>", unsafe_allow_html=True)
    nav_l, nav_c, nav_r = st.columns([1, 2, 1])

    with nav_l:
        if step > 0 and step < last_step:
            if st.button("← Back", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()

    with nav_r:
        if step < last_step - 1:
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.step += 1
                st.rerun()
        elif step == last_step - 1:
            if st.button("Run credit check →", type="primary", use_container_width=True):
                st.session_state.result = None
                st.session_state.step = last_step
                st.rerun()
        elif step == last_step:
            if st.button("New application", type="primary", use_container_width=True):
                _reset_application()
                st.rerun()

    with nav_c:
        st.markdown(
            f'<p class="footer-note">Step {step + 1} of {len(STEPS)} · '
            f"{currency} · Shino Loan Approval Studio</p>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
