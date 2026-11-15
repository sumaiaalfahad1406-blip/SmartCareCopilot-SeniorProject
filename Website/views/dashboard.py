"""'Today' page: a greeting, a one-line summary, recent notes and the patient list."""

import html
from datetime import date, datetime

import streamlit as st

from helpers import show_html, av
from actions import open_patient


def _age(dob: str) -> str:
    try:
        b = date.fromisoformat(dob)
    except (TypeError, ValueError):
        return "—"
    t = date.today()
    return str(t.year - b.year - ((t.month, t.day) < (b.month, b.day)))


def _greeting() -> str:
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def dashboard_page():
    ss = st.session_state
    patients = ss.patients
    doc = ss.doctor
    surname = doc["name"].replace("Dr.", "").strip().split()[-1] if doc.get("name") else ""

    # Every consultation that has at least one entry, newest first (list order is newest-first).
    notes = []
    for p in patients:
        for c in ss.consultations.get(p["id"], []):
            if c["messages"]:
                notes.append((p, c))
    open_count = sum(len(ss.consultations.get(p["id"], [])) for p in patients)

    if patients:
        summary = (f"You have <b>{_plural(len(patients), 'patient')}</b> on your list and "
                   f"<b>{_plural(open_count, 'consultation')}</b> on file. "
                   "Pick a patient to continue a note, or start a new one.")
    else:
        summary = "Your list is empty. Add your first patient from the panel on the left."

    if notes:
        notes_html = "".join(
            f'<div class="note-item"><div class="note-date">{html.escape(c["date"])}</div>'
            f'<div><div class="note-title">{html.escape(c["title"])}</div>'
            f'<div class="note-who">{html.escape(p["name"])} · {len(c["messages"])} entries</div></div></div>'
            for p, c in notes[:4]
        )
    else:
        notes_html = '<div class="note-empty">No notes written yet.</div>'

    show_html(f"""
    <div class="dash-date">{datetime.now().strftime('%A, %d %B %Y')}</div>
    <div class="dash-h">{_greeting()}, Dr. {html.escape(surname)}.</div>
    <div class="dash-s">{summary}</div>
    <div class="dash-sec"><span class="t">Recent notes</span><span class="lbl">last {min(len(notes), 4)}</span></div>
    <div class="note-list">{notes_html}</div>
    <div class="dash-sec"><span class="t">Patient list</span><span class="lbl">{_plural(len(patients), 'patient')}</span></div>
    """)

    widths = [2.4, 0.7, 0.9, 1.2, 1.4, 1]
    with st.container(border=True, key="rec_card"):
        head = st.columns(widths)
        for col, label in zip(head, ["Patient", "Age", "Sex", "Born", "Last seen", ""]):
            show_html(f'<span class="rec-th">{label}</span>', col)
        if not patients:
            show_html('<div class="note-empty">No patients yet.</div>')
        for p in patients[:12]:
            c = st.columns(widths, vertical_alignment="center")
            show_html(f'<div class="rec-name">{av(p["name"], 28, 12)}{html.escape(p["name"])}</div>', c[0])
            show_html(f'<div class="rec-cell mono">{_age(p.get("dob"))}</div>', c[1])
            show_html(f'<div class="rec-cell">{html.escape(p.get("gender") or "—")}</div>', c[2])
            show_html(f'<div class="rec-cell mono">{html.escape(p.get("dob") or "—")}</div>', c[3])
            show_html(f'<div class="rec-cell">{html.escape(p["last_active"])}</div>', c[4])
            c[5].button("Open chart →", key=f"rec_p{p['id']}", type="tertiary",
                        on_click=open_patient, args=(p["id"],))
