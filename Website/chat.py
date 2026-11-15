"""Consultation rendering: doctor entries and Copilot notes, styled like a clinical file.

Doctor messages are shown as chart entries; Copilot replies are shown as a
draft clinical note. The model's markdown ("### Heading", "- bullet",
"**bold**") is turned into simple HTML, and an optional "Evidence:" line
(added by model.py) is shown as a small footnote.
"""

import html
import json
import re

from helpers import esc, bold

DRAFT_LINE = "Draft prepared by Copilot for clinician review. Not a final diagnosis."


def files_html(files) -> str:
    out = ""
    for f in files or []:
        if f["type"].startswith("image/"):
            out += (f'<img class="bubble-img" src="data:{f["type"]};base64,{f["data"]}" '
                    f'alt="{html.escape(f["name"])}"/>')
        elif f["type"].startswith("audio/"):
            out += f'<div class="bubble-file">voice note · {html.escape(f["name"])}</div>'
        else:
            out += f'<div class="bubble-file">attachment · {html.escape(f["name"])}</div>'
    return out


def note_html(text: str) -> tuple[str, str]:
    """Turn the model's markdown-ish report into note HTML.

    Returns (body_html, evidence_html).
    """
    body, evidence, bullets = [], [], []

    def flush():
        if bullets:
            body.append("<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.lower().startswith("evidence:"):
            flush()
            evidence.append(bold(esc(line[len("evidence:"):].strip())))
            continue
        if line == "---":
            flush()
            continue
        m = re.match(r"^#{1,6}\s+(.*)$", line)
        if m:
            flush()
            body.append(f'<div class="note-h">{bold(esc(m.group(1)))}</div>')
            continue
        m = re.match(r"^[-*•]\s+(.*)$", line)
        if m:
            bullets.append(bold(esc(m.group(1))))
            continue
        flush()
        body.append(f"<div>{bold(esc(line))}</div>")
    flush()

    ev = ""
    if evidence:
        ev = '<div class="evidence">' + "<br/>".join(evidence) + "</div>"
    return "".join(body), ev


def top3_html(raw: str) -> str:
    """Render validated model JSON as a differential-diagnosis clinical panel."""
    try:
        data = json.loads(raw[len("TOP3_JSON:"):])
        diagnoses = data["diagnoses"]
        if len(diagnoses) != 3:
            raise ValueError("Expected three diagnoses")
        cards = []
        for i, item in enumerate(diagnoses, 1):
            label = html.escape(str(item["diagnosis"]).replace("_", " ").title())
            explanation = html.escape(str(item.get("explanation", "")))
            cards.append(f'<div class="dx-card"><div class="dx-number">0{i}</div><div class="dx-content"><div class="dx-overline">Differential {i}</div><div class="dx-title">{label}</div><div class="dx-reason">{explanation}</div></div></div>')
        evaluation = html.escape(str(data.get("further_evaluation", "")))
        translation = html.escape(str(data.get("translation", "")))
        trans = f'<div class="dx-translation"><b>English translation used</b><p>{translation}</p></div>' if translation else ""
        return (f'<div class="dx-panel"><div class="dx-eyebrow">SMARTCARE / CLINICAL INTELLIGENCE</div>'
                f'<div class="dx-heading">Differential diagnosis <span>Top 3</span></div>'
                f'<div class="dx-intro">Three ranked possibilities for clinician review — not confirmed diagnoses.</div>'
                + "".join(cards) + f'<div class="dx-follow"><div class="dx-follow-title">Further clinical evaluation</div><div>{evaluation}</div></div>'
                + trans + '<div class="dx-disclaimer">Research prototype · Verify all findings independently · Seek urgent assessment for emergency symptoms</div></div>')
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return '<div class="dx-disclaimer">The differential report could not be displayed.</div>'


def bubbles_html(msgs) -> str:
    out = []
    first_doc = True
    for m in msgs:
        t = html.escape(m.get("time", ""))
        fh = files_html(m.get("files"))
        if m["role"] == "user":
            who = "Presenting complaint" if first_doc else "Clinician entry"
            first_doc = False
            out.append(
                f'<div class="entry doc"><div class="entry-meta"><span class="who">{who}</span>'
                f'<span class="rule"></span><span class="when">{t}</span></div>'
                f'<div class="body">{esc(m["text"]) or "&nbsp;"}{fh}</div></div>')
        else:
            text = m.get("text") or ""
            if text.lstrip().startswith("⚠️") or text.startswith("Error from model"):
                msg = text.lstrip().removeprefix("⚠️").strip()
                out.append(
                    f'<div class="entry ai warn"><div class="entry-meta"><span class="who">Copilot could not answer</span>'
                    f'<span class="rule"></span><span class="when">{t}</span></div>'
                    f'<div class="body">{bold(esc(msg))}</div></div>')
                continue
            body, ev = (top3_html(text), "") if text.startswith("TOP3_JSON:") else note_html(text)
            out.append(
                f'<div class="entry ai"><div class="entry-meta"><span class="who">Copilot · draft note</span>'
                f'<span class="rule"></span><span class="when">{t}</span></div>'
                f'<div class="body">{body}{fh}{ev}<div class="draft">{DRAFT_LINE}</div></div></div>')
    return "".join(out)
