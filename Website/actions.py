"""Callbacks that mutate session state: navigation, CRUD, chat send, logout."""

from datetime import datetime

import streamlit as st

from state import get_consult, get_patient, now_time
from styles import TYPING_HTML
from helpers import show_html
from chat import bubbles_html
from model import run_ai_query


def go_dashboard():
    st.session_state.page = "dashboard"
    st.session_state.cur_pid = None
    st.session_state.cur_cid = None


def go_profile():
    st.session_state.page = "profile"


def open_patient(pid):
    st.session_state.page = "patient"
    st.session_state.cur_pid = pid
    st.session_state.cur_cid = None


def select_consult(cid):
    st.session_state.cur_cid = cid


def new_consult():
    ss = st.session_state
    if not ss.cur_pid or ss.cur_pid not in ss.consultations:
        return
    now = datetime.now()
    cid = "c_" + ss.cur_pid + "_" + now.strftime("%Y%m%d%H%M%S")
    ss.consultations[ss.cur_pid].insert(
        0, {"id": cid, "title": "New Consultation", "date": now.strftime("%b %d, %Y"), "messages": []}
    )
    ss.cur_cid = cid


def request_dialog(name, **kwargs):
    st.session_state.dialog = {"name": name, **kwargs}


def delete_patient(pid):
    ss = st.session_state
    ss.patients = [p for p in ss.patients if p["id"] != pid]
    ss.consultations.pop(pid, None)
    if ss.cur_pid == pid:
        go_dashboard()


def update_patient(pid, name, dob, gender):
    """Edit an existing patient's core details."""
    p = get_patient(pid)
    if p:
        p["name"] = name
        p["dob"] = dob
        p["gender"] = gender


def delete_consult(pid, cid):
    ss = st.session_state
    ss.consultations[pid] = [c for c in ss.consultations.get(pid, []) if c["id"] != cid]
    if ss.cur_cid == cid:
        ss.cur_cid = None


def rename_consult(pid, cid, new_title):
    c = get_consult(pid, cid)
    if c and new_title.strip():
        c["title"] = new_title.strip()


def start_edit_profile():
    ss = st.session_state
    ss.editing_profile = True
    ss.ef_name = ss.doctor.get("name", "")
    ss.ef_spec = ss.doctor.get("specialty", "")
    ss.ef_email = ss.doctor.get("email", "")
    ss.ef_hosp = ss.doctor.get("hospital", "")


def cancel_edit_profile():
    st.session_state.editing_profile = False


def save_profile():
    ss = st.session_state
    ss.doctor.update({
        "name": ss.ef_name.strip(),
        "specialty": ss.ef_spec.strip(),
        "email": ss.ef_email.strip(),
        "hospital": ss.ef_hosp.strip(),
    })
    ss.editing_profile = False


def logout():
    """Log the doctor out and return to the login screen.

    Session data (patients/consultations) is kept in memory until the
    browser tab's session actually ends — there's no persistence layer yet
    (see README). Logging back in during the same session will show the
    same data, not a fresh seed.
    """
    ss = st.session_state
    ss.logged_in = False
    ss.page = "dashboard"
    ss.cur_pid = None
    ss.cur_cid = None


def send_message(text: str, files: list, box):
    """Add the doctor's message, call the model, store the answer, then rerun."""
    ss = st.session_state
    pid, cid = ss.cur_pid, ss.cur_cid
    consult = get_consult(pid, cid)
    patient = get_patient(pid) or {}
    if not consult or (not text and not files):
        return

    t = now_time()
    user_msg = {"role": "user", "text": text, "time": t, "files": files}
    consult["messages"].append(user_msg)
    if len(consult["messages"]) == 1:
        consult["title"] = (text or ", ".join(f["name"] for f in files))[:60].strip()

    history = []
    for m in consult["messages"]:
        txt = m["text"]
        if m.get("files"):
            txt = (txt + "\n" if txt else "") + "📎 " + ", ".join(f["name"] for f in m["files"])
        history.append({"role": m["role"], "text": txt})

    with box:
        show_html(bubbles_html([user_msg]))
        typing = st.empty()
        show_html(TYPING_HTML, typing)
        try:
            ai_text = run_ai_query(text, patient, history, files)
        except Exception as e:  # noqa: BLE001
            ai_text = f"Error from model: {e}"
        typing.empty()

    consult["messages"].append({"role": "ai", "text": ai_text, "time": now_time()})
    st.rerun()
