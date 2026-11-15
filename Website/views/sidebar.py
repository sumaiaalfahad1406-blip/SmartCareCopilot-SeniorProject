"""Left sidebar: wordmark, new-patient button, search, patient list, nav, profile, logout."""

import streamlit as st

from config import PT_LIST_HEIGHT
from helpers import show_html, av, md_escape, initials
from actions import request_dialog, open_patient, go_dashboard, go_profile, logout


def sidebar():
    ss = st.session_state
    with st.sidebar:
        show_html('<div class="sb-brand"><div class="sb-name">SmartCare</div>'
                  '<div class="sb-tag">Clinical workspace</div></div>')
        st.button("New patient", type="primary", use_container_width=True, key="btn_new_patient",
                  on_click=request_dialog, args=("add_patient",))
        q = st.text_input("Search", placeholder="Find a patient", label_visibility="collapsed", key="search")
        show_html('<div class="sec-lbl">Patient list</div>')

        patients = [p for p in ss.patients if q.strip().lower() in p["name"].lower()]
        with st.container(height=PT_LIST_HEIGHT, border=False):
            if not patients:
                show_html('<div class="cempty">Nobody by that name.</div>')
            for p in patients:
                active = ss.page == "patient" and ss.cur_pid == p["id"]
                row = st.columns([1.1, 4, 0.9], vertical_alignment="center")
                show_html(av(p["name"], 30, 13), row[0])
                row[1].button(f"**{md_escape(p['name'])}**  \nseen {md_escape(p['last_active'])}",
                              key=f"{'pta' if active else 'pti'}_{p['id']}", type="tertiary",
                              use_container_width=True, on_click=open_patient, args=(p["id"],))
                row[2].button("×", key=f"pdel_{p['id']}", type="tertiary", help="Remove patient",
                              on_click=request_dialog, args=("delete_patient",),
                              kwargs={"pid": p["id"], "pt_name": p["name"]})

        st.button("Today", use_container_width=True, key="btn_dash", on_click=go_dashboard)
        st.divider()
        doc = ss.doctor
        f = st.columns([1, 4], vertical_alignment="center")
        show_html(av(initials(doc["name"]), 30, 12, "#1F2A44"), f[0])
        f[1].button(f"**{md_escape(doc['name'])}**  \n{md_escape(doc['specialty'])}",
                    key="doc_btn", type="tertiary", use_container_width=True, on_click=go_profile)
        st.button("Sign out", use_container_width=True, key="btn_logout", on_click=logout)
