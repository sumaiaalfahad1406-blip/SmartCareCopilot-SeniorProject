"""Modal dialogs: add / edit / delete patient, rename / delete consultation."""

import uuid
from datetime import date

import streamlit as st

from state import get_patient
from actions import delete_patient, delete_consult, update_patient, rename_consult, open_patient
from helpers import md_escape


@st.dialog("New patient")
def add_patient_dialog():
    name = st.text_input("Patient Name *", placeholder="Full name")
    dob = st.date_input("Date of Birth *", value=None, min_value=date(1900, 1, 1),
                        max_value=date.today(), format="YYYY-MM-DD")
    gender = st.selectbox("Gender *", ["Male", "Female", "Other"], index=None, placeholder="Select gender...")
    err = st.empty()
    c1, c2 = st.columns(2)
    if c1.button("Cancel", use_container_width=True, key="add_cancel"):
        st.rerun()
    if c2.button("Add patient", type="primary", use_container_width=True, key="add_create"):
        name = (name or "").strip()
        if not name:
            err.markdown('<div class="modal-err">Patient name is required.</div>', unsafe_allow_html=True)
        elif not dob:
            err.markdown('<div class="modal-err">Date of birth is required.</div>', unsafe_allow_html=True)
        elif not gender:
            err.markdown('<div class="modal-err">Gender is required.</div>', unsafe_allow_html=True)
        else:
            pid = "p_" + uuid.uuid4().hex[:8]
            st.session_state.patients.insert(
                0, {"id": pid, "name": name, "dob": dob.isoformat(), "gender": gender, "last_active": "just now"})
            st.session_state.consultations[pid] = []
            open_patient(pid)
            st.rerun()


@st.dialog("Edit patient details")
def edit_patient_dialog(pid):
    p = get_patient(pid)
    if not p:
        st.rerun()
        return
    name = st.text_input("Patient Name *", value=p["name"])
    try:
        dob_val = date.fromisoformat(p["dob"]) if p.get("dob") else None
    except ValueError:
        dob_val = None
    dob = st.date_input("Date of Birth *", value=dob_val, min_value=date(1900, 1, 1),
                        max_value=date.today(), format="YYYY-MM-DD")
    genders = ["Male", "Female", "Other"]
    gidx = genders.index(p["gender"]) if p.get("gender") in genders else None
    gender = st.selectbox("Gender *", genders, index=gidx, placeholder="Select gender...")
    err = st.empty()
    c1, c2 = st.columns(2)
    if c1.button("Cancel", use_container_width=True, key="edit_cancel"):
        st.rerun()
    if c2.button("Save changes", type="primary", use_container_width=True, key="edit_save"):
        name = (name or "").strip()
        if not name:
            err.markdown('<div class="modal-err">Patient name is required.</div>', unsafe_allow_html=True)
        elif not dob:
            err.markdown('<div class="modal-err">Date of birth is required.</div>', unsafe_allow_html=True)
        elif not gender:
            err.markdown('<div class="modal-err">Gender is required.</div>', unsafe_allow_html=True)
        else:
            update_patient(pid, name, dob.isoformat(), gender)
            st.rerun()


@st.dialog("Remove patient")
def confirm_delete_patient(pid, name):
    st.markdown(f"Are you sure you want to delete **{md_escape(name)}** and all their consultations? "
                "This cannot be undone.")
    c1, c2 = st.columns(2)
    if c1.button("Cancel", use_container_width=True, key="dp_cancel"):
        st.rerun()
    if c2.button("Delete", type="primary", use_container_width=True, key="confirm_del_btn"):
        delete_patient(pid)
        st.rerun()


@st.dialog("Rename consultation")
def rename_consult_dialog(pid, cid, title):
    new_title = st.text_input("Consultation title", value=title)
    err = st.empty()
    c1, c2 = st.columns(2)
    if c1.button("Cancel", use_container_width=True, key="rc_cancel"):
        st.rerun()
    if c2.button("Save", type="primary", use_container_width=True, key="rc_save"):
        if not (new_title or "").strip():
            err.markdown("<div class=\"modal-err\">Title can't be empty.</div>", unsafe_allow_html=True)
        else:
            rename_consult(pid, cid, new_title)
            st.rerun()


@st.dialog("Delete consultation")
def confirm_delete_consult(pid, cid, title):
    st.markdown(f"Delete \"**{md_escape(title)}**\"? This cannot be undone.")
    c1, c2 = st.columns(2)
    if c1.button("Cancel", use_container_width=True, key="dc_cancel"):
        st.rerun()
    if c2.button("Delete", type="primary", use_container_width=True, key="confirm_del_btn"):
        delete_consult(pid, cid)
        st.rerun()


def open_requested_dialog():
    """Dialogs are opened from here (outside the sidebar/columns) after the page is drawn."""
    req = st.session_state.pop("dialog", None)
    if not req:
        return
    if req["name"] == "add_patient":
        add_patient_dialog()
    elif req["name"] == "edit_patient":
        edit_patient_dialog(req["pid"])
    elif req["name"] == "delete_patient":
        confirm_delete_patient(req["pid"], req["pt_name"])
    elif req["name"] == "rename_consult":
        rename_consult_dialog(req["pid"], req["cid"], req["title"])
    elif req["name"] == "delete_consult":
        confirm_delete_consult(req["pid"], req["cid"], req["title"])
