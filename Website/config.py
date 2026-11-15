"""
Configuration & constants for SmartCare Copilot.
"""

CHAT_HEIGHT = 420   # fallback; styles.py sizes it to the screen        # height (px) of the scrolling chat window
PT_LIST_HEIGHT = 300     # height (px) of the patient list in the sidebar
FILE_TYPES = ["png", "jpg", "jpeg", "gif", "webp", "pdf", "doc", "docx", "txt", "csv"]

# Muted, earthy chart-tab colours (warm clinic file theme)
AVATAR_COLORS = ["#3F5E7A", "#5E7D63", "#8C5E3C", "#7A6A8F", "#B5543C", "#A07A2C"]

# Demo login credentials (replace with real auth before production use).
# NOTE: login now requires an EXACT match on both fields — earlier drafts
# accidentally let a blank email + blank password log in too.
DEMO_EMAIL = "demo@smartcare.ai"
DEMO_PASSWORD = "demo1234"
