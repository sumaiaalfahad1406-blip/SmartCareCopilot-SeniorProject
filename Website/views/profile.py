"""Doctor profile page: view / edit info, a short record of activity."""

import html

import streamlit as st

from state import get_stats
from helpers import show_html, initials
from actions import go_dashboard, start_edit_profile, save_profile, cancel_edit_profile


def profile_page():
    ss = st.session_state
    doc = ss.doctor
    s = get_stats()

    st.button("← Back to today", type="tertiary", key="prof_back", on_click=go_dashboard)
    left, right, _ = st.columns([1, 0.9, 0.5])

    with left:
        with st.container(border=True, key="prof_card"):
            show_html(f"""
            <div class="prof-top">
              <div class="prof-av">{html.escape(initials(doc['name']))}</div>
              <div class="prof-name-wrap"><div class="pn">{html.escape(doc['name'])}</div>
              <div class="ps">{html.escape(doc['specialty'])} · {html.escape(doc.get('hospital') or '')}</div></div>
            </div>
            """)
            if ss.editing_profile:
                st.text_input("Full name", key="ef_name", placeholder="Dr. ...")
                st.text_input("Specialty", key="ef_spec", placeholder="e.g. Internal Medicine")
                st.text_input("Email", key="ef_email", placeholder="you@hospital.org")
                st.text_input("Hospital", key="ef_hosp", placeholder="Hospital name")
                b1, b2 = st.columns(2)
                b1.button("Save changes", type="primary", key="prof_save", on_click=save_profile,
                          use_container_width=True)
                b2.button("Cancel", key="prof_cancel", on_click=cancel_edit_profile, use_container_width=True)
            else:
                for label, key in [("Full name", "name"), ("Specialty", "specialty"),
                                   ("Email", "email"), ("Hospital", "hospital")]:
                    show_html(f'<div class="pf-row"><label class="pf-label">{label}</label>'
                              f'<div class="pf-value">{html.escape(doc.get(key) or "—")}</div></div>')
                st.button("Edit details", key="prof_edit", on_click=start_edit_profile)

    with right:
        with st.container(border=True, key="prof_stats"):
            show_html(f"""
            <div class="prof-h">Your record</div>
            <div class="prof-stat-row"><span class="prof-stat-label">Patients on your list</span><span class="prof-stat-val">{s['total_patients']}</span></div>
            <div class="prof-stat-row"><span class="prof-stat-label">Consultations</span><span class="prof-stat-val">{s['ai_consultations']}</span></div>
            <div class="prof-stat-row"><span class="prof-stat-label">Entries written</span><span class="prof-stat-val">{s['total_messages']}</span></div>
            """)
