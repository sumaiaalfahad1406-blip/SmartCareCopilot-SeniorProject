"""
Interactive, image-based symptom selector for Streamlit.

This module is SELF-CONTAINED and does not touch your medical AI model.
It only (1) shows your infographic, (2) lets the user pick symptom cards, and
(3) writes English text into YOUR existing text-input widget's session-state key.

Public API
----------
render_symptom_selector_button(input_key)   -> draws the "Select Symptoms" button
apply_pending_symptom_text(input_key)       -> call BEFORE your text widget is created
merge_symptoms_into_text(text, labels, cfg) -> pure helper (no Streamlit needed)
SYMPTOMS, SymptomTextConfig                 -> configuration
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import streamlit as st

# --------------------------------------------------------------------------- #
# 1. Configuration
# --------------------------------------------------------------------------- #

# Path is resolved relative to this file, so it works no matter where you
# launch `streamlit run` from.
IMAGE_PATH = Path(__file__).resolve().parent.parent / "assets" / "symptom_infographic.png"

# Pixel size of the infographic the coordinates below were measured on.
# Coordinates are scaled by (actual size / reference size), so a resized
# copy of the same artwork still works. If you replace the artwork with a
# different layout, re-measure the boxes.
REFERENCE_SIZE = (1024, 1536)  # (width, height)


@dataclass(frozen=True)
class Symptom:
    id: str
    label: str
    # (x0, y0, x1, y1) card boundary in REFERENCE_SIZE pixels
    bbox: tuple[int, int, int, int]


# Card boundaries measured from the real card borders (not equal slices).
_COLS = [(14, 256), (267, 508), (519, 760), (771, 1011)]
_ROWS = [(137, 390), (405, 660), (675, 931), (945, 1205), (1223, 1483)]
_LABELS = [
    ("fever", "Fever"), ("headache", "Headache"),
    ("stomachache", "Stomachache"), ("nausea", "Nausea"),
    ("cough", "Cough"), ("sore_throat", "Sore Throat"),
    ("shortness_of_breath", "Shortness of Breath"), ("chest_pain", "Chest Pain"),
    ("dizziness", "Dizziness"), ("earache", "Earache"),
    ("toothache", "Toothache"), ("runny_nose", "Runny Nose"),
    ("sneeze", "Sneeze"), ("muscle_pain", "Muscle Pain"),
    ("fatigue", "Fatigue"), ("loss_of_appetite", "Loss of Appetite"),
    ("diarrhea", "Diarrhea"), ("constipation", "Constipation"),
    ("rash", "Rash"), ("chills", "Chills"),
]

SYMPTOMS: tuple[Symptom, ...] = tuple(
    Symptom(
        id=sid,
        label=label,
        bbox=(_COLS[i % 4][0], _ROWS[i // 4][0], _COLS[i % 4][1], _ROWS[i // 4][1]),
    )
    for i, (sid, label) in enumerate(_LABELS)
)
SYMPTOM_BY_ID = {s.id: s for s in SYMPTOMS}


@dataclass(frozen=True)
class SymptomTextConfig:
    """
    Wording of the text written into the input field.
    ADAPT THESE to whatever format your medical AI model expects.
    """
    first_template: str = "I have {symptoms}."          # input was empty
    additional_template: str = "I also have {symptoms}."  # input already had text
    lowercase_labels: bool = True       # "Sore Throat" -> "sore throat"
    separator: str = " "                # between existing text and new sentence
    fix_terminal_punctuation: bool = True  # add "." to existing text lacking .!?


DEFAULT_TEXT_CONFIG = SymptomTextConfig()

# --------------------------------------------------------------------------- #
# 2. Pure helpers (no Streamlit state) - easy to unit-test
# --------------------------------------------------------------------------- #

def join_natural(items: Sequence[str]) -> str:
    """['a'] -> 'a'; ['a','b'] -> 'a and b'; ['a','b','c'] -> 'a, b, and c'."""
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def find_symptoms_in_text(text: str) -> set[str]:
    """IDs of symptoms whose English label already appears in `text`."""
    found = set()
    for s in SYMPTOMS:
        pattern = r"(?<![A-Za-z])" + re.escape(s.label) + r"(?![A-Za-z])"
        if re.search(pattern, text or "", flags=re.IGNORECASE):
            found.add(s.id)
    return found


def merge_symptoms_into_text(
    current_text: str,
    selected_labels: Iterable[str],
    config: SymptomTextConfig = DEFAULT_TEXT_CONFIG,
) -> str:
    """
    Return `current_text` with the selected symptoms appended naturally.

    - Existing text is preserved (only a missing final period may be added).
    - Symptoms already mentioned in the text are skipped (no duplicates).
    - Empty / fully-duplicate selection returns the text unchanged.
    """
    current_text = current_text or ""
    already = find_symptoms_in_text(current_text)
    label_to_id = {s.label.lower(): s.id for s in SYMPTOMS}

    new_labels, seen = [], set()
    for label in selected_labels:
        sid = label_to_id.get(label.strip().lower())
        if sid is None or sid in already or sid in seen:
            continue
        seen.add(sid)
        new_labels.append(label.strip())
    if not new_labels:
        return current_text

    shown = [l.lower() if config.lowercase_labels else l for l in new_labels]
    phrase = join_natural(shown)

    if not current_text.strip():
        return config.first_template.format(symptoms=phrase)

    base = current_text.rstrip()
    if config.fix_terminal_punctuation and not re.search(r"[.!?\u061f]$", base):
        base += "."
    return base + config.separator + config.additional_template.format(symptoms=phrase)


def hit_test(x: float, y: float, shown_w: float, shown_h: float) -> str | None:
    """
    Map a click on the DISPLAYED image to a symptom id.
    (x, y) are in displayed pixels; shown_w/h is the displayed size. Works at
    any display scale because everything is normalised to the reference size.
    """
    if not shown_w or not shown_h:
        return None
    rx = x / shown_w * REFERENCE_SIZE[0]
    ry = y / shown_h * REFERENCE_SIZE[1]
    for s in SYMPTOMS:
        x0, y0, x1, y1 = s.bbox
        if x0 <= rx <= x1 and y0 <= ry <= y1:
            return s.id
    return None  # click landed in a gap / the title banner


# --------------------------------------------------------------------------- #
# 3. Image overlay (the PNG file on disk is never modified)
# --------------------------------------------------------------------------- #

@st.cache_resource(show_spinner=False)
def _load_base_image():
    from PIL import Image
    if not IMAGE_PATH.exists():
        return None
    return Image.open(IMAGE_PATH).convert("RGBA")


def render_overlay(base, selected_ids: set[str]):
    """Copy of the infographic with a green tint, thick border and check badge
    on selected cards. The original artwork pixels stay untouched elsewhere."""
    from PIL import Image, ImageDraw
    out = base.copy()
    sx = base.width / REFERENCE_SIZE[0]
    sy = base.height / REFERENCE_SIZE[1]
    tint = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tint)
    for s in SYMPTOMS:
        if s.id not in selected_ids:
            continue
        x0, y0, x1, y1 = (s.bbox[0] * sx, s.bbox[1] * sy, s.bbox[2] * sx, s.bbox[3] * sy)
        d.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=(34, 160, 90, 60),
                            outline=(22, 140, 75, 255), width=8)
        r = 20 * sx  # check badge, bottom-right corner (keeps card titles readable)
        cx, cy = x1 - r - 10 * sx, y1 - r - 10 * sy
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(22, 140, 75, 255),
                  outline=(255, 255, 255, 255), width=3)
        d.line([(cx - 0.5 * r, cy), (cx - 0.1 * r, cy + 0.45 * r), (cx + 0.55 * r, cy - 0.4 * r)],
               fill=(255, 255, 255, 255), width=max(3, int(5 * sx)), joint="curve")
    return Image.alpha_composite(out, tint).convert("RGB")


# --------------------------------------------------------------------------- #
# 4. Streamlit state + UI
# --------------------------------------------------------------------------- #

# Namespaced session-state keys (won't collide with your own keys)
K_OPEN = "symsel_open"              # selector currently open?
K_TEMP = "symsel_temp_ids"          # UNCONFIRMED selection (discarded on cancel)
K_ALREADY = "symsel_already_ids"    # symptoms already present in the text on open
K_CONFIRMED = "symsel_confirmed_ids"  # everything the user has ever confirmed
K_PENDING = "symsel_pending_text"   # staged text, applied before the widget renders
K_OPENS = "symsel_open_count"       # increments per open -> fresh widget keys
K_LASTCLICK = "symsel_last_click"   # de-duplicates click events across reruns

try:
    from streamlit_image_coordinates import streamlit_image_coordinates as _img_click
    HAS_IMAGE_CLICK = True
except ImportError:  # fallback UI is used instead
    _img_click = None
    HAS_IMAGE_CLICK = False

_dialog = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)


def apply_pending_symptom_text(input_key: str) -> None:
    """
    CALL THIS BEFORE creating your text widget (same run).

    Streamlit forbids writing st.session_state[widget_key] after that widget
    exists in the current run. The selector therefore stages the new text,
    triggers a rerun, and this function applies it at the top of that rerun.
    """
    pending = st.session_state.get(K_PENDING)
    if pending and pending.get("key") == input_key:
        st.session_state[input_key] = pending["text"]
        del st.session_state[K_PENDING]


def _open_selector(input_key: str) -> None:
    ss = st.session_state
    already = find_symptoms_in_text(ss.get(input_key, ""))
    ss[K_ALREADY] = already
    ss[K_TEMP] = set(already)          # re-opening shows what is already in the text
    ss[K_OPENS] = ss.get(K_OPENS, 0) + 1
    ss[K_LASTCLICK] = None
    ss[K_OPEN] = True


def _close(rerun_full: bool = True) -> None:
    st.session_state[K_OPEN] = False
    if rerun_full:
        st.rerun()  # full rerun closes the dialog


def _local_rerun() -> None:
    """Re-run just the dialog when possible (keeps the page behind it still)."""
    if _dialog is not None:
        try:
            st.rerun(scope="fragment")
            return
        except TypeError:  # very old Streamlit without scope=
            pass
    st.rerun()


def _toggle(sid: str) -> None:
    sel = st.session_state[K_TEMP]
    sel.symmetric_difference_update({sid})


def _checkbox_changed(sid: str, widget_key: str) -> None:
    sel = st.session_state[K_TEMP]
    (sel.add if st.session_state[widget_key] else sel.discard)(sid)


def _image_click_widget(img, key: str):
    # Different versions of streamlit-image-coordinates name the "fit width" option differently.
    for kwargs in ({"width": "stretch"}, {"use_column_width": "always"}, {}):
        try:
            return _img_click(img, key=key, **kwargs)
        except TypeError:
            continue
    return None


def _selector_body(input_key: str, config: SymptomTextConfig) -> None:
    ss = st.session_state
    sel: set = ss[K_TEMP]
    already: set = ss[K_ALREADY]
    n_open = ss[K_OPENS]

    # --- Infographic (click to toggle) ---------------------------------- #
    base = _load_base_image()
    if base is None:
        st.error(f"Infographic not found at `{IMAGE_PATH}`. Place your image at "
                 "`assets/symptom_infographic.png` (relative to the project root). "
                 "You can still choose symptoms from the list below.")
    elif HAS_IMAGE_CLICK:
        st.caption("Tap a card to select it. Tap again to deselect.")
        click = _image_click_widget(render_overlay(base, sel), key=f"symsel_img_{n_open}")
        if click and click.get("unix_time") != ss[K_LASTCLICK]:
            ss[K_LASTCLICK] = click.get("unix_time")
            sid = hit_test(click["x"], click["y"], click["width"], click["height"])
            if sid:
                _toggle(sid)
                _local_rerun()
    else:
        st.warning("`streamlit-image-coordinates` is not installed, so the image is "
                   "display-only. Use the list below to select symptoms.")
        st.image(render_overlay(base, sel), use_container_width=True)

    # --- Accessible / mobile-friendly list (same selection state) --------- #
    with st.expander("Or choose from a list", expanded=(base is None or not HAS_IMAGE_CLICK)):
        cols = st.columns(2)
        for i, s in enumerate(SYMPTOMS):
            wkey = f"symsel_cb_{n_open}_{s.id}"
            ss[wkey] = s.id in sel  # safe: this widget is not created yet in this run
            cols[i % 2].checkbox(s.label, key=wkey, on_change=_checkbox_changed,
                                 args=(s.id, wkey))

    # --- Summary + count --------------------------------------------------- #
    ordered = [s for s in SYMPTOMS if s.id in sel]
    new = [s for s in ordered if s.id not in already]
    st.markdown(f"**Selected symptoms: {len(ordered)}**")
    if ordered:
        st.write(", ".join(s.label for s in ordered))
    else:
        st.caption("Nothing selected yet.")
    if already and (already & sel):
        st.caption("Symptoms already written in your text are shown as selected and "
                   "won't be added twice.")

    # --- Actions ------------------------------------------------------------ #
    c1, c2, c3 = st.columns(3)
    if c1.button("Clear Selection", key=f"symsel_clear_{n_open}", use_container_width=True):
        sel.clear()
        _local_rerun()
    if c2.button("Cancel", key=f"symsel_cancel_{n_open}", use_container_width=True):
        ss[K_TEMP] = set()   # discard unconfirmed changes; the text input is untouched
        _close()
    if c3.button("Yes, Add Symptoms", key=f"symsel_ok_{n_open}", type="primary",
                 use_container_width=True, disabled=not new):
        new_text = merge_symptoms_into_text(ss.get(input_key, ""), [s.label for s in new], config)
        ss[K_PENDING] = {"key": input_key, "text": new_text}   # staged, NOT written to the widget
        ss[K_CONFIRMED] = ss.get(K_CONFIRMED, set()) | {s.id for s in new}
        _close()
    if not new:
        st.caption("Select at least one new symptom to enable “Yes, Add Symptoms”.")


def render_symptom_selector_button(
    input_key: str,
    config: SymptomTextConfig = DEFAULT_TEXT_CONFIG,
    button_label: str = "Select Symptoms",
    icon: str | None = "🩺",
) -> None:
    """
    Draw the "Select Symptoms" button and handle the dialog.

    input_key: the st.session_state key of YOUR existing text widget.
    Never calls your model; it only stages text for that widget.
    """
    if st.button(button_label, icon=icon, key="symsel_open_btn", use_container_width=True,
                 help="Pick symptoms from the illustrated chart"):
        _open_selector(input_key)
        if _dialog is not None:
            @_dialog("Select Your Symptoms", width="large")
            def _show():
                _selector_body(input_key, config)
            _show()
            return

    # Fallback for Streamlit without st.dialog: inline panel
    if _dialog is None and st.session_state.get(K_OPEN):
        with st.container(border=True):
            st.subheader("Select Your Symptoms")
            _selector_body(input_key, config)
