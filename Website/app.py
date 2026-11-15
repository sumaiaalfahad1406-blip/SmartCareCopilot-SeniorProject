"""
SmartCare Copilot - Streamlit Edition
======================================
Run:
    pip install "streamlit>=1.43"
    streamlit run app.py

Recommended: create  .streamlit/config.toml  next to this file with:
    [theme]
    base = "light"
    primaryColor = "#2563EB"

HOW TO CONNECT YOUR MODEL:
    Open model.py and edit run_ai_query() — that's the only file the rest
    of the app depends on for AI output. Nothing else needs to change.

PROJECT LAYOUT — see README.md for the full breakdown. Short version:
    config.py, seed_data.py, state.py, helpers.py, styles.py, chat.py  -> shared building blocks
    model.py     -> connect your AI model here
    actions.py   -> callbacks that mutate state (navigation, CRUD, send message, logout)
    dialogs.py   -> modal dialogs (add/edit/delete patient, rename/delete consult)
    views/       -> one file per screen (login, sidebar, dashboard, profile, patient)

    Note: the screens live in "views/", not "pages/" — Streamlit auto-turns a
    folder literally named "pages" into its own multi-page navigation, which
    would clash with the session_state-based navigation used here. Don't
    rename that folder to "pages".
"""

import streamlit as st
import streamlit.components.v1 as components

from state import init_state
from styles import CSS
from dialogs import open_requested_dialog
from views.login import login_page
from views.sidebar import sidebar
from views.dashboard import dashboard_page
from views.profile import profile_page
from views.patient import patient_page

st.set_page_config(
    page_title="SmartCare Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Streamlit remembers a collapsed sidebar in the browser. On the first page of
# each session we open it again, so the patient list is always visible at start.
_OPEN_SIDEBAR_JS = """
<script>
(function () {
  const doc = window.parent.document;
  let tries = 0;
  const timer = setInterval(function () {
    tries += 1;
    const bar = doc.querySelector('section[data-testid="stSidebar"]');
    if (bar && bar.getAttribute("aria-expanded") === "true") { clearInterval(timer); return; }
    const btn = doc.querySelector('[data-testid="stExpandSidebarButton"]') ||
                doc.querySelector('[data-testid="stSidebarCollapsedControl"] button') ||
                doc.querySelector('[data-testid="collapsedControl"] button');
    if (btn) { btn.click(); clearInterval(timer); }
    if (tries > 30) clearInterval(timer);
  }, 100);
})();
</script>
"""


def _open_sidebar_once():
    if not st.session_state.get("_sidebar_opened"):
        st.session_state["_sidebar_opened"] = True
        components.html(_OPEN_SIDEBAR_JS, height=0)


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()

    if not st.session_state.logged_in:
        login_page()
        return

    sidebar()
    _open_sidebar_once()
    page = st.session_state.page
    if page == "profile":
        profile_page()
    elif page == "patient":
        patient_page()
    else:
        dashboard_page()

    open_requested_dialog()


main()
