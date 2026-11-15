"""Blue and white SmartCare login page. Authentication logic unchanged."""
import base64
import html
from pathlib import Path
import streamlit as st
from config import DEMO_EMAIL, DEMO_PASSWORD
from styles import LOGIN_CSS
from helpers import show_html
from actions import go_dashboard


def login_page():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    show_html('<div class="blue-login-marker"></div>')
    hero, form_col = st.columns([1.08, 0.92], gap="large")
    with hero:
        show_html('''
        <div class="blue-brand"><span class="blue-brand-icon"><svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><path d="M32 53C21 45 8 35 8 23C8 12 23 7 32 19C41 7 56 12 56 23C56 35 43 45 32 53Z" fill="white" opacity=".95"/><path d="M10 31H23L28 20L35 42L40 30H54" stroke="#1689de" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/></svg></span><span>SmartCare<br/>Copilot</span></div>
        <div class="blue-eyebrow">Clinical decision support · Top-3 insights</div>
        <h1 class="blue-title">Smarter Insights.<br/><span>Better Care.</span></h1>
        <p class="blue-desc">Find similar patient cases, explore three potential diagnoses, and support more informed clinical decisions.</p>
        <div class="blue-feature"><span>Top-3 differential diagnoses</span><span>Multilingual symptom input</span></div>
        ''')
        picture = Path(__file__).resolve().parent.parent / "assets" / "doctor_patient.png"
        if picture.exists():
            encoded = base64.b64encode(picture.read_bytes()).decode("ascii")
            show_html(f'<img class="blue-illustration" src="data:image/png;base64,{encoded}" alt="Doctor discussing care with an older patient"/>')
    with form_col:
        show_html('''<div class="blue-card-top"></div><div class="blue-card-icon">♡</div><div class="blue-card-heading">Welcome Back</div><div class="blue-card-sub">Sign in to SmartCare Copilot</div>''')
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            pw = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
        if submitted:
            if email.strip() == DEMO_EMAIL and pw.strip() == DEMO_PASSWORD:
                st.session_state.logged_in = True
                go_dashboard()
                st.rerun()
            else:
                show_html('<div class="blue-error">Incorrect email or password. Please try again.</div>')
        show_html(f'<div class="blue-demo">Demo access: <b>{html.escape(DEMO_EMAIL)}</b> / <b>{html.escape(DEMO_PASSWORD)}</b></div><div class="blue-card-bottom">⌁ ♡</div>')
