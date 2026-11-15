"""Small formatting / HTML-escaping helpers used across every page."""

import html
import re

import streamlit as st

from config import AVATAR_COLORS


def avatar_color(name: str) -> str:
    return AVATAR_COLORS[ord(name[0]) % len(AVATAR_COLORS)] if name else AVATAR_COLORS[0]


def av(name: str, size: int = 34, fs: int = 13, bg: str = None) -> str:
    bg = bg or avatar_color(name)
    return (f'<div class="av" style="background:{bg};width:{size}px;height:{size}px;font-size:{fs}px">'
            f'{html.escape(name[:1])}</div>')


def initials(name: str) -> str:
    return "".join(w[0] for w in name.split() if w)[:2].upper() or "D"


def esc(t: str) -> str:
    """Escape text for HTML (also keeps line breaks)."""
    t = html.escape(t or "", quote=False).replace("$", "&#36;")
    return t.replace("\n", "<br/>")


def bold(t: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", t)


def md_escape(t: str) -> str:
    """Escape markdown characters (used for button labels / dialog text)."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!$~<>|])", r"\\\1", t or "")


def short(t: str, n: int) -> str:
    return t if len(t) <= n else t[: n - 1] + "…"


def compact(s: str) -> str:
    """Collapse multi-line HTML into a single line (blank lines break st.markdown HTML blocks)."""
    return "".join(line.strip() for line in s.splitlines())


def show_html(s: str, target=None):
    (target or st).markdown(compact(s), unsafe_allow_html=True)
