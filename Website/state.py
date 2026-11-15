"""Session-state initialization and small read-only accessors, shared by every page."""

from copy import deepcopy
from datetime import datetime

import streamlit as st

from seed_data import SEED_PATIENTS, SEED_CONSULTATIONS, SEED_DOCTOR


def init_state():
    ss = st.session_state
    if "initialized" in ss:
        return
    ss.initialized = True
    ss.logged_in = False
    ss.patients = deepcopy(SEED_PATIENTS)
    ss.consultations = deepcopy(SEED_CONSULTATIONS)
    ss.doctor = deepcopy(SEED_DOCTOR)
    ss.page = "dashboard"          # dashboard | profile | patient
    ss.cur_pid = None
    ss.cur_cid = None
    ss.editing_profile = False
    ss.audio_n = 0                 # bump to reset the voice recorder widget


def get_patient(pid):
    return next((p for p in st.session_state.patients if p["id"] == pid), None)


def get_consult(pid, cid):
    return next((c for c in st.session_state.consultations.get(pid, []) if c["id"] == cid), None)


def get_stats() -> dict:
    ss = st.session_state
    return {
        "total_patients": len(ss.patients),
        "ai_consultations": sum(len(v) for v in ss.consultations.values()),
        "total_messages": sum(len(c["messages"]) for v in ss.consultations.values() for c in v),
    }


def now_time() -> str:
    return datetime.now().strftime("%I:%M %p").lstrip("0")
