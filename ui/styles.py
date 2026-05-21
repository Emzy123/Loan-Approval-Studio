"""Global CSS for the loan approval UI."""

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --ink: #0f172a;
                --ink-muted: #64748b;
                --surface: #ffffff;
                --canvas: #f1f5f9;
                --accent: #0ea5e9;
                --accent-deep: #0284c7;
                --success: #059669;
                --success-soft: #d1fae5;
                --danger: #dc2626;
                --danger-soft: #fee2e2;
                --border: #e2e8f0;
                --shadow: 0 4px 24px rgba(15, 23, 42, 0.08);
                --radius: 16px;
            }

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
            }

            .stApp {
                background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 48%, #f1f5f9 100%);
            }

            header[data-testid="stHeader"] {
                background: transparent;
            }

            .block-container {
                padding-top: 1.5rem;
                max-width: 1100px;
            }

            .hero {
                background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #0c4a6e 100%);
                border-radius: 20px;
                padding: 2rem 2.25rem;
                color: #f8fafc;
                box-shadow: var(--shadow);
                margin-bottom: 1.5rem;
            }

            .hero-badge {
                display: inline-block;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                background: rgba(14, 165, 233, 0.25);
                border: 1px solid rgba(125, 211, 252, 0.35);
                padding: 0.35rem 0.75rem;
                border-radius: 999px;
                margin-bottom: 0.75rem;
            }

            .hero h1 {
                font-size: 2rem;
                font-weight: 800;
                margin: 0 0 0.5rem 0;
                letter-spacing: -0.03em;
            }

            .hero p {
                margin: 0;
                color: #cbd5e1;
                font-size: 1rem;
                line-height: 1.6;
                max-width: 52rem;
            }

            .stepper {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin: 1.25rem 0 1.75rem 0;
            }

            .step {
                flex: 1;
                min-width: 140px;
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 0.85rem 1rem;
                text-align: center;
                transition: all 0.2s ease;
            }

            .step.active {
                border-color: var(--accent);
                box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
            }

            .step.done {
                background: #f0f9ff;
                border-color: #bae6fd;
            }

            .step-num {
                font-size: 0.7rem;
                font-weight: 700;
                color: var(--ink-muted);
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }

            .step-label {
                font-size: 0.92rem;
                font-weight: 700;
                color: var(--ink);
                margin-top: 0.2rem;
            }

            .card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 1.35rem 1.5rem;
                box-shadow: var(--shadow);
                margin-bottom: 1rem;
            }

            .card-title {
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                color: var(--ink-muted);
                margin-bottom: 0.35rem;
            }

            .card-heading {
                font-size: 1.15rem;
                font-weight: 700;
                color: var(--ink);
                margin: 0 0 0.25rem 0;
            }

            .card-sub {
                font-size: 0.88rem;
                color: var(--ink-muted);
                margin: 0 0 1rem 0;
            }

            .metric-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                background: #f8fafc;
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0.35rem 0.85rem;
                font-size: 0.82rem;
                font-weight: 600;
                color: var(--ink);
            }

            .verdict {
                border-radius: 20px;
                padding: 1.75rem;
                text-align: center;
                color: white;
                box-shadow: var(--shadow);
            }

            .verdict.approved {
                background: linear-gradient(145deg, #047857 0%, #059669 100%);
            }

            .verdict.rejected {
                background: linear-gradient(145deg, #b91c1c 0%, #dc2626 100%);
            }

            .verdict-label {
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                opacity: 0.9;
            }

            .verdict-title {
                font-size: 2.25rem;
                font-weight: 800;
                margin: 0.35rem 0;
                letter-spacing: -0.02em;
            }

            .verdict-confidence {
                font-size: 1rem;
                opacity: 0.95;
            }

            .review-row {
                display: flex;
                justify-content: space-between;
                padding: 0.65rem 0;
                border-bottom: 1px solid var(--border);
                font-size: 0.92rem;
            }

            .review-row:last-child { border-bottom: none; }
            .review-key { color: var(--ink-muted); font-weight: 500; }
            .review-val { color: var(--ink); font-weight: 700; }

            .sidebar-brand {
                font-size: 1.1rem;
                font-weight: 800;
                color: var(--ink);
                letter-spacing: -0.02em;
            }

            .trust-item {
                font-size: 0.85rem;
                color: var(--ink-muted);
                margin: 0.35rem 0;
            }

            div[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border-right: 1px solid var(--border);
            }

            div[data-testid="stSidebar"] .block-container {
                padding-top: 1.5rem;
            }

            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #0284c7, #0ea5e9);
                border: none;
                border-radius: 12px;
                font-weight: 700;
                letter-spacing: 0.02em;
                padding: 0.7rem 1.2rem;
                box-shadow: 0 8px 20px rgba(14, 165, 233, 0.35);
            }

            .stButton > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #0369a1, #0284c7);
            }

            .stButton > button[kind="secondary"] {
                border-radius: 12px;
                font-weight: 600;
                border: 1px solid var(--border);
            }

            .footer-note {
                text-align: center;
                color: var(--ink-muted);
                font-size: 0.8rem;
                margin-top: 2rem;
                padding-bottom: 1rem;
            }

            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
