"""Patient page: chart header, consultations list, and the consultation note."""

import base64
import html
from datetime import date

import streamlit as st

from config import CHAT_HEIGHT, FILE_TYPES
from state import get_patient, get_consult
from helpers import show_html, av, md_escape, initials, short
from chat import bubbles_html
from actions import go_dashboard, new_consult, select_consult, request_dialog, send_message
from components.symptom_selector import render_symptom_selector_button, K_PENDING
from arabic_pipeline import transcribe_audio

# Key used by the sign-language symptom picker to stage text (no text widget is
# needed: the picked symptoms are sent straight to the model).
SYMPTOM_KEY = "symptom_picker_text"


def _age(dob: str) -> str:
    try:
        b = date.fromisoformat(dob)
    except (TypeError, ValueError):
        return ""
    t = date.today()
    return f"{t.year - b.year - ((t.month, t.day) < (b.month, b.day))} y"


def patient_page():
    ss = st.session_state
    if ss.pop("voice_clear_on_next_run", False):
        ss.pop("voice_draft", None)
    p = get_patient(ss.cur_pid)
    if not p:
        go_dashboard()
        st.rerun()
    doc = ss.doctor

    # ── Chart header ──
    with st.container(key="chat_hdr"):
        h = st.columns([0.5, 5.5, 0.8, 3], vertical_alignment="center")
        h[0].button("←", key="btn_back", type="tertiary", on_click=go_dashboard, help="Back to today")
        meta = " · ".join(x for x in [_age(p.get("dob")), p.get("gender") or "",
                                      f"born {p['dob']}" if p.get("dob") else ""] if x)
        show_html(f'<span class="ch-name">{html.escape(p["name"])}</span>'
                  f'<span class="ch-meta">{html.escape(meta)}</span>', h[1])
        h[2].button("Edit", key="pt_edit_btn", type="tertiary", help="Edit patient details",
                    on_click=request_dialog, args=("edit_patient",), kwargs={"pid": p["id"]})
        show_html(f'<div class="h-doc-wrap"><div class="h-doc">attending<br/><b>{html.escape(doc["name"])}</b></div>'
                  f'{av(initials(doc["name"]), 30, 12, "#1F2A44")}</div>', h[3])

    consults = ss.consultations.get(p["id"], [])
    consult = get_consult(p["id"], ss.cur_cid) if ss.cur_cid else None

    left, right = st.columns([1, 3.4])

    # ── Consultations panel ──
    with left:
        with st.container(border=True, key="cpanel"):
            show_html('<div class="cp-t">Consultations</div>'
                      f'<div class="cp-sub">{len(consults)} on file</div>')
            st.button("+ New consultation", key="btn_new_consult", on_click=new_consult,
                      use_container_width=True, help="Start a new consultation")
            if not consults:
                show_html('<div class="cempty">Nothing on file yet.</div>')
            for c in consults:
                active = c["id"] == ss.cur_cid
                row = st.columns([4, 1, 1], vertical_alignment="center")
                label = (f"**{md_escape(short(c['title'], 26))}**  \n"
                         f"{md_escape(c['date'])} · {len(c['messages'])} entries")
                row[0].button(label, key=f"{'cta' if active else 'cti'}_{c['id']}", type="tertiary",
                              use_container_width=True, on_click=select_consult, args=(c["id"],))
                row[1].button("✎", key=f"cren_{c['id']}", type="tertiary", help="Rename",
                              on_click=request_dialog, args=("rename_consult",),
                              kwargs={"pid": p["id"], "cid": c["id"], "title": c["title"]})
                row[2].button("×", key=f"cdel_{c['id']}", type="tertiary", help="Delete",
                              on_click=request_dialog, args=("delete_consult",),
                              kwargs={"pid": p["id"], "cid": c["id"], "title": c["title"]})

    # ── Consultation note ──
    with right:
        box = st.container(height=CHAT_HEIGHT, border=False, key="chat_box")
        with box:
            if consult is None:
                show_html("""
                <div class="empty-chat"><div class="et">No consultation open.</div>
                <div class="es">Choose one on the left, or start a new one. You can describe the patient
                by voice, by typing, or with the selectable symptom cards.</div></div>
                """)
                mid = st.columns([1, 1, 1])
                mid[1].button("Start a consultation", type="primary", key="btn_start_new",
                              on_click=new_consult, use_container_width=True)
            elif consult["messages"]:
                show_html(bubbles_html(consult["messages"]))
            else:
                show_html("""
                <div class="empty-chat"><div class="et">A blank page.</div>
                <div class="es">Start with the presenting complaint: what the patient tells you, in their words.</div></div>
                """)

        if consult is not None:
            show_html('<div class="inp-lbl">Add to the note</div>')
            tools = st.columns([2.2, 1.9, 2.8], vertical_alignment="top")
            with tools[0]:
                with st.expander("Voice symptoms — live microphone", expanded=True):
                    language = st.selectbox(
                        "Recording language", ["Arabic", "English"], key="voice_language"
                    )
                    st.caption("Click Start, speak, then Stop. No separate recording file needed.")
                    try:
                        from streamlit_mic_recorder import mic_recorder
                    except ImportError:
                        st.error(
                            "Live microphone component is not installed. In Terminal run: "
                            "python -m pip install streamlit-mic-recorder"
                        )
                        recorded = None
                    else:
                        recorded = mic_recorder(
                            start_prompt="🎙️ Start recording",
                            stop_prompt="⏹️ Stop recording",
                            just_once=True,
                            use_container_width=True,
                            key="smartcare_live_mic",
                        )
                    # Persist the captured audio across Streamlit reruns.
                    # The recorder may return None when Transcribe is clicked.
                    if recorded and recorded.get("bytes"):
                        new_audio_id = recorded.get("id")
                        if new_audio_id is None or new_audio_id != ss.get("live_audio_id"):
                            ss["live_audio_bytes"] = recorded["bytes"]
                            ss["live_audio_id"] = new_audio_id
                    saved_audio = ss.get("live_audio_bytes")
                    if saved_audio:
                        st.audio(saved_audio, format="audio/wav")
                        if st.button("Transcribe live recording", key="btn_transcribe_live"):
                            try:
                                with st.spinner("Whisper is transcribing..."):
                                    transcript = transcribe_audio(
                                        saved_audio,
                                        "ar" if language == "Arabic" else "en",
                                    )
                                if transcript.strip():
                                    ss["voice_draft"] = transcript
                                    st.rerun()
                                else:
                                    st.warning("No speech detected. Try again.")
                            except Exception as exc:
                                st.error(f"Could not transcribe audio: {exc}")
            if ss.get("voice_draft"):
                st.caption("Review and edit the transcription before running MedRAG.")
                edited = st.text_area("Transcribed symptoms", key="voice_draft")
                csend, cclear = st.columns([1, 1])
                if csend.button("Send symptoms to MedRAG", type="primary",
                                key="btn_send_transcription"):
                    if edited.strip():
                        ss["voice_pending_send"] = edited.strip()
                        ss["voice_clear_on_next_run"] = True
                        st.rerun()
                if cclear.button("Discard transcription", key="btn_discard_transcription"):
                    ss["voice_clear_on_next_run"] = True
                    st.rerun()
            with tools[1]:
                render_symptom_selector_button(SYMPTOM_KEY, button_label="Symptom cards", icon=None)

        prompt = st.chat_input(
            "Type symptoms, results, or a question…",
            key="chat_in", accept_file="multiple", file_type=FILE_TYPES, disabled=consult is None,
        )
        show_html('<div class="disc">Copilot drafts; the clinician decides. Always verify before acting.</div>')

        # Process the transcribed voice message in the normal consultation flow.
        voice_pending = ss.pop("voice_pending_send", None)
        if voice_pending and consult is not None:
            send_message(voice_pending, [], box)

        pending = ss.get(K_PENDING)
        if pending and pending.get("key") == SYMPTOM_KEY:
            del ss[K_PENDING]
            if consult is not None:
                send_message(pending["text"], [], box)

        if prompt and consult is not None:
            text = (prompt["text"] or "").strip()
            files = [
                {"name": f.name, "type": f.type or "application/octet-stream",
                 "data": base64.b64encode(f.getvalue()).decode()}
                for f in (prompt["files"] or [])
            ]
            if files:
                st.warning("MedRAG does not analyze attachments in this version. "
                           "Enter the clinical symptoms as text.")
            if text:
                send_message(text, files, box)
