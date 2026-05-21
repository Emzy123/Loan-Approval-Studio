"""Reusable UI fragments."""

from __future__ import annotations

import html

import streamlit as st


STEPS = ["Currency", "Profile", "Financials", "Review", "Decision"]


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-badge">Intelligent credit decisioning</div>
            <h1>Loan Approval Studio</h1>
            <p>
                Submit a complete application in guided steps. Our machine learning
                engine evaluates risk instantly and returns a transparent approval decision
                with confidence scores.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(current: int) -> None:
    """current: 0-based index of active step."""
    parts = []
    for i, name in enumerate(STEPS):
        cls = "step"
        if i < current:
            cls += " done"
        elif i == current:
            cls += " active"
        parts.append(
            f'<div class="{cls}">'
            f'<div class="step-num">Step {i + 1}</div>'
            f'<div class="step-label">{html.escape(name)}</div>'
            f"</div>"
        )
    st.markdown(f'<div class="stepper">{"".join(parts)}</div>', unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    sub = f'<p class="card-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<div class="card-title">{html.escape(title)}</div>{sub}',
        unsafe_allow_html=True,
    )


def render_review_table(rows: list[tuple[str, str]]) -> None:
    body = "".join(
        f'<div class="review-row"><span class="review-key">{html.escape(k)}</span>'
        f'<span class="review-val">{html.escape(v)}</span></div>'
        for k, v in rows
    )
    st.markdown(f'<div class="card">{body}</div>', unsafe_allow_html=True)


def render_verdict(label: str, confidence: float, probs: dict[str, float]) -> None:
    approved = label == "Approved"
    css = "approved" if approved else "rejected"
    icon = "✓" if approved else "✕"
    st.markdown(
        f"""
        <div class="verdict {css}">
            <div class="verdict-label">Decision</div>
            <div class="verdict-title">{icon} {html.escape(label)}</div>
            <div class="verdict-confidence">{confidence:.1%} model confidence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_df = __import__("pandas").DataFrame(
        {"Outcome": list(probs.keys()), "Probability": [p * 100 for p in probs.values()]}
    )
    st.markdown("##### Probability breakdown")
    st.bar_chart(chart_df.set_index("Outcome"), color="#0ea5e9")


def cibil_hint(score: int) -> str:
    if score >= 750:
        return "Excellent — strongly supports approval"
    if score >= 650:
        return "Good — moderate positive signal"
    if score >= 550:
        return "Fair — may require stronger income/assets"
    return "Weak — elevated risk profile"


def render_sidebar_currency(currency_code: str) -> None:
    from ui.currencies import CURRENCIES, format_money

    c = CURRENCIES[currency_code]
    st.markdown("**Display currency**")
    st.markdown(
        f'<span class="metric-pill">{c["flag"]} {currency_code} · {c["name"]}</span>',
        unsafe_allow_html=True,
    )
    st.caption("Amounts are entered in this currency. The model converts to INR internally.")
    st.markdown(
        f'<p class="trust-item">Example: {format_money(1_000_000, currency_code)}</p>',
        unsafe_allow_html=True,
    )


def render_sidebar_brand(model_name: str, show_chart: bool, chart_path: str | None) -> None:
    st.markdown('<p class="sidebar-brand">Shino Credit</p>', unsafe_allow_html=True)
    st.caption("Enterprise loan decision support")
    st.divider()
    st.markdown("**Active model**")
    st.markdown(f'<span class="metric-pill">🤖 {html.escape(model_name)}</span>', unsafe_allow_html=True)
    st.markdown(
        '<p class="trust-item">✓ Real-time inference</p>'
        '<p class="trust-item">✓ Explainable probabilities</p>'
        '<p class="trust-item">✓ Validated on historical portfolio</p>',
        unsafe_allow_html=True,
    )
    if show_chart and chart_path:
        st.divider()
        st.markdown("**Risk drivers**")
        st.image(chart_path, use_container_width=True)
