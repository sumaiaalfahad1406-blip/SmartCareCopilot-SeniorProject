"""All CSS for the app (main theme + login screen) and the 'reviewing' indicator.

Design direction: "warm clinic file". Paper background, ink-blue text, a single
terracotta accent, a serif for headings (Fraunces), a humanist sans for body
text (IBM Plex Sans) and a monospace for small chart-style labels (IBM Plex Mono).
No gradients, no emoji icons, no floating stat cards.
"""

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{
  --paper:#F6F1E9;--sheet:#FFFDF8;--ink:#1F2A44;--ink-2:#3B4660;
  --muted:#7D7466;--faint:#A79E90;--line:#E4DACB;--line-2:#D6CAB7;
  --accent:#B5543C;--accent-soft:#F4E4DC;--sage:#5E7D63;--danger:#A33A2B;
  /* legacy names still used in a few inline styles */
  --pri:var(--ink);--pri-d:#141C30;--pri-l:#ECE6DA;--bg:var(--paper);--white:var(--sheet);
  --border:var(--line);--text:var(--ink);--light:var(--faint);--error:var(--danger);--success:var(--sage);
  --serif:'Fraunces',Georgia,'Times New Roman',serif;
  --sans:'IBM Plex Sans',-apple-system,'Segoe UI',sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
}
html,body,.stApp,.stApp p,.stApp label,.stApp input,.stApp textarea,.stApp button,
.stApp [data-testid="stMarkdownContainer"]{font-family:var(--sans)}
.stApp{background:var(--paper);color:var(--ink)}
#MainMenu,footer{visibility:hidden}
/* "Open sidebar" arrow: always visible, light square with a dark arrow */
[data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"],[data-testid="collapsedControl"]{visibility:visible!important;display:flex!important;opacity:1!important;z-index:1000}
[data-testid="stSidebarCollapsedControl"] button,[data-testid="stExpandSidebarButton"],[data-testid="collapsedControl"] button{background:var(--sheet)!important;border:1px solid var(--line-2)!important;border-radius:6px!important;width:38px;height:38px}
[data-testid="stSidebarCollapsedControl"] button:hover,[data-testid="stExpandSidebarButton"]:hover,[data-testid="collapsedControl"] button:hover{border-color:var(--ink)!important}
[data-testid="stSidebarCollapsedControl"] *,[data-testid="stExpandSidebarButton"] *,[data-testid="collapsedControl"] *{color:var(--ink)!important;fill:var(--ink)!important;opacity:1!important;visibility:visible!important}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding:1.8rem 2.4rem 1rem!important;max-width:100%!important}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:3px}

/* ── small shared bits ── */
.lbl{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.serif{font-family:var(--serif)}

/* ── Buttons ── */
.stApp button{border-radius:6px!important;box-shadow:none!important}
[data-testid^="stBaseButton-primary"]{background:var(--ink)!important;border:1px solid var(--ink)!important;color:#fff!important;font-weight:500!important}
[data-testid^="stBaseButton-primary"] p{color:#fff!important;font-weight:500}
[data-testid^="stBaseButton-primary"]:hover{background:#141C30!important;border-color:#141C30!important}
[data-testid^="stBaseButton-secondary"]{background:transparent;border:1px solid var(--line-2);font-weight:500;color:var(--ink)}
[data-testid^="stBaseButton-secondary"]:hover{background:var(--sheet);border-color:var(--ink);color:var(--ink)}
[data-testid^="stBaseButton-tertiary"]{color:var(--ink)}
[data-testid^="stBaseButton-tertiary"]:hover{color:var(--accent)}

/* ── Inputs ── */
div[data-baseweb="input"],div[data-baseweb="textarea"],div[data-baseweb="select"]>div{border:1px solid var(--line-2)!important;border-radius:6px!important;background:var(--sheet)!important}
div[data-baseweb="input"]:focus-within,div[data-baseweb="textarea"]:focus-within{border-color:var(--ink)!important}
.stApp label p{font-size:12.5px;font-weight:500;color:var(--ink-2)}
[data-testid="stChatInput"]{border:1px solid var(--line-2)!important;border-radius:8px!important;background:var(--sheet)!important}
[data-testid="stChatInput"]:focus-within{border-color:var(--ink)!important}
[data-testid="stChatInput"] textarea{color:var(--ink)!important;background:transparent!important}
[data-testid="stChatInput"] textarea::placeholder{color:var(--faint)!important}
[data-testid="stDialog"] [role="dialog"]{background:var(--sheet);border-radius:10px}
[data-testid="stDialog"] h2{font-family:var(--serif)!important;font-weight:500!important;color:var(--ink)}
hr{border-color:var(--line)!important}
/* Readable form fields everywhere (also inside dialogs), whatever the system theme */
.stApp input,.stApp textarea,[data-testid="stDialog"] input,[data-testid="stDialog"] textarea{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;background:transparent!important;caret-color:var(--ink)}
.stApp input::placeholder,.stApp textarea::placeholder{color:var(--faint)!important;-webkit-text-fill-color:var(--faint)!important;opacity:1}
div[data-baseweb="select"] *{color:var(--ink)}
div[data-baseweb="select"] [aria-selected="false"],div[data-baseweb="select"] input::placeholder{color:var(--faint)}
[data-testid="stDialog"] label p,[data-testid="stDialog"] [data-testid="stMarkdownContainer"] p,[data-testid="stWidgetLabel"] p{color:var(--ink-2)!important}
[data-testid="stDialog"] [role="dialog"] > div:first-child,[data-testid="stDialog"] [role="dialog"] h2,[data-testid="stDialog"] [role="dialog"] h2 *{color:var(--ink)!important;font-family:var(--serif)!important;font-weight:500!important}
[data-testid="stDialog"] [role="dialog"] button[aria-label="Close"] svg{color:var(--muted)!important}
ul[role="listbox"],div[data-baseweb="popover"] ul{background:var(--sheet)!important}
ul[role="listbox"] li{color:var(--ink)!important}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{background:#EFE8DC;border-right:1px solid var(--line)}
/* fixed width only while the sidebar is open, so it can still collapse fully */
section[data-testid="stSidebar"][aria-expanded="true"]{width:268px!important;min-width:268px!important}
section[data-testid="stSidebar"][aria-expanded="true"] > div{width:268px!important}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding:.6rem .8rem 1rem}
.sb-brand{padding:4px 4px 14px}
.sb-name{font-family:var(--serif);font-size:22px;font-weight:500;color:var(--ink);letter-spacing:-.01em;line-height:1}
.sb-tag{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-top:5px}
.sec-lbl{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding:10px 4px 4px;border-top:1px solid var(--line-2);margin-top:6px}
.av{border-radius:6px;color:#fff;display:flex;align-items:center;justify-content:center;font-family:var(--serif);font-weight:500;flex-shrink:0}

/* list items (patients / consultations) */
[class*="st-key-pti_"] button,[class*="st-key-pta_"] button,
[class*="st-key-cti_"] button,[class*="st-key-cta_"] button{justify-content:flex-start;text-align:left;padding:.4rem .6rem;height:auto;min-height:0;width:100%;border:1px solid transparent;transition:background .15s,border-color .15s}
[class*="st-key-pti_"] button:hover,[class*="st-key-cti_"] button:hover{background:rgba(255,253,248,.7)}
[class*="st-key-pti_"] button p,[class*="st-key-pta_"] button p,
[class*="st-key-cti_"] button p,[class*="st-key-cta_"] button p{text-align:left;font-size:11.5px;color:var(--muted);line-height:1.45;margin:0}
[class*="st-key-pti_"] button p strong,[class*="st-key-pta_"] button p strong,
[class*="st-key-cti_"] button p strong,[class*="st-key-cta_"] button p strong{font-size:13.5px;font-weight:500;color:var(--ink)}
[class*="st-key-pta_"] button,[class*="st-key-cta_"] button{background:var(--sheet);border-color:var(--line-2);box-shadow:inset 3px 0 0 var(--accent)!important}
[class*="st-key-cti_"] button{border-bottom:1px solid var(--line)}
[class*="st-key-pdel_"],[class*="st-key-cdel_"],[class*="st-key-cren_"]{opacity:0;transition:opacity .15s}
div[data-testid="stHorizontalBlock"]:hover [class*="st-key-pdel_"],
div[data-testid="stHorizontalBlock"]:hover [class*="st-key-cdel_"],
div[data-testid="stHorizontalBlock"]:hover [class*="st-key-cren_"]{opacity:1}
[class*="st-key-pdel_"] button,[class*="st-key-cdel_"] button{color:var(--faint);padding:0 .3rem;min-height:1.8rem}
[class*="st-key-pdel_"] button:hover,[class*="st-key-cdel_"] button:hover{color:var(--danger)}
[class*="st-key-cren_"] button{color:var(--faint);padding:0 .3rem;min-height:1.8rem}
[class*="st-key-cren_"] button:hover{color:var(--ink)}
.st-key-btn_dash button,.st-key-btn_logout button{justify-content:flex-start;border:none!important;background:transparent!important;padding-left:.5rem}
.st-key-btn_dash button p,.st-key-btn_logout button p{font-size:13px;color:var(--ink-2)}
.st-key-btn_logout button:hover p{color:var(--danger)}
.st-key-doc_btn button{justify-content:flex-start;text-align:left;height:auto;padding:.3rem .5rem}
.st-key-doc_btn button p{text-align:left;font-size:11px;color:var(--muted);line-height:1.4}
.st-key-doc_btn button p strong{font-size:12.5px;font-weight:500;color:var(--ink)}
.st-key-pt_edit_btn button{color:var(--muted);padding:0 .4rem}
.st-key-pt_edit_btn button:hover{color:var(--ink)}

/* ═══ DASHBOARD ═══ */
.dash-date{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
.dash-h{font-family:var(--serif);font-size:38px;font-weight:400;letter-spacing:-.015em;line-height:1.1;color:var(--ink);margin-bottom:10px}
.dash-s{font-size:15px;color:var(--ink-2);max-width:620px;line-height:1.6;margin-bottom:34px}
.dash-s b{font-weight:600;color:var(--ink)}
.dash-sec{display:flex;align-items:baseline;justify-content:space-between;border-bottom:1px solid var(--line-2);padding-bottom:8px;margin:6px 0 4px}
.dash-sec .t{font-family:var(--serif);font-size:20px;font-weight:500;color:var(--ink)}
.note-list{margin-bottom:30px}
.note-item{display:grid;grid-template-columns:110px 1fr;gap:18px;padding:14px 0;border-bottom:1px dashed var(--line-2)}
.note-item:last-child{border-bottom:none}
.note-date{font-family:var(--mono);font-size:11px;color:var(--muted);padding-top:3px}
.note-title{font-size:14.5px;color:var(--ink);font-weight:500;margin-bottom:2px}
.note-who{font-size:12.5px;color:var(--muted)}
.note-empty{font-size:14px;color:var(--muted);padding:16px 0;font-style:italic;font-family:var(--serif)}
.st-key-rec_card{background:var(--sheet);border:1px solid var(--line)!important;border-radius:8px}
.rec-th{font-family:var(--mono);font-size:10px;letter-spacing:.1em;color:var(--muted);text-transform:uppercase}
.rec-name{display:flex;align-items:center;gap:10px;font-weight:500;font-size:14.5px;color:var(--ink)}
.rec-cell{font-size:13px;color:var(--ink-2)}
.rec-cell.mono{font-family:var(--mono);font-size:12px}
.rec-badge{font-size:12.5px;color:var(--ink-2)}
[class*="st-key-rec_p"] button p{font-size:12.5px;color:var(--accent)}

/* ═══ PROFILE ═══ */
.st-key-prof_card,.st-key-prof_stats{background:var(--sheet);border:1px solid var(--line)!important;border-radius:8px}
.prof-top{display:flex;align-items:center;gap:16px;padding:6px 4px 18px;border-bottom:1px solid var(--line);margin-bottom:18px}
.prof-av{width:58px;height:58px;border-radius:8px;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-family:var(--serif);font-size:22px;flex-shrink:0}
.prof-name-wrap .pn{font-family:var(--serif);font-size:24px;font-weight:500;color:var(--ink);line-height:1.15}
.prof-name-wrap .ps{font-size:13px;color:var(--muted);margin-top:3px}
.pf-row{margin-bottom:16px}
.pf-label{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.1em;color:var(--muted);margin-bottom:4px;text-transform:uppercase}
.pf-value{font-size:14.5px;color:var(--ink)}
.prof-h{font-family:var(--serif);font-size:19px;font-weight:500;margin-bottom:10px;color:var(--ink)}
.prof-stat-row{display:flex;align-items:baseline;justify-content:space-between;padding:11px 0;border-bottom:1px dashed var(--line-2)}
.prof-stat-row:last-child{border-bottom:none}
.prof-stat-label{font-size:13.5px;color:var(--ink-2)}
.prof-stat-val{font-family:var(--serif);font-size:20px;color:var(--ink)}

/* ═══ PATIENT PAGE ═══ */
.st-key-chat_hdr{background:var(--sheet);border:1px solid var(--line);border-radius:8px;padding:.55rem 1.1rem;margin-bottom:.7rem;box-shadow:inset 4px 0 0 var(--accent)}
.ch-name{font-family:var(--serif);font-size:24px;font-weight:500;color:var(--ink);letter-spacing:-.01em}
.ch-meta{display:block;font-family:var(--mono);font-size:11.5px;color:var(--muted);margin-top:2px;letter-spacing:.02em}
.h-doc-wrap{display:flex;align-items:center;justify-content:flex-end;gap:10px}
.h-doc{font-size:11.5px;color:var(--muted);text-align:right;line-height:1.5}
.h-doc b{color:var(--ink);font-weight:500}
.st-key-cpanel{background:var(--sheet);border:1px solid var(--line)!important;border-radius:8px}
.cp-t{font-family:var(--serif);font-size:18px;font-weight:500;color:var(--ink)}
.st-key-btn_new_consult{margin:6px 0 4px}
.st-key-btn_new_consult button p{white-space:nowrap;font-size:13px}
.cp-sub{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.cempty{color:var(--muted);font-size:13px;padding:18px 6px;font-family:var(--serif);font-style:italic}

/* consultation "sheet": fits the screen so the input stays visible without scrolling */
.st-key-chat_box{height:calc(100vh - 400px)!important;min-height:240px!important;max-height:none!important}
[data-testid="stAppDeployButton"],.stAppDeployButton{display:none!important}
/* consultation "sheet" */
.st-key-chat_box{background:var(--sheet);border:1px solid var(--line);border-radius:8px;padding:6px 10px!important;
  background-image:linear-gradient(var(--sheet) 0,var(--sheet) 100%)}
.entry{margin:14px 6px 22px;max-width:760px}
.entry-meta{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.entry-meta .who{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase}
.entry-meta .when{font-family:var(--mono);font-size:10.5px;color:var(--faint)}
.entry-meta .rule{flex:1;height:1px;background:var(--line)}
.entry.doc .who{color:var(--ink-2)}
.entry.doc .body{font-size:14.5px;line-height:1.65;color:var(--ink);padding-left:12px;border-left:2px solid var(--ink)}
.entry.ai .who{color:var(--accent)}
.entry.ai .body{font-size:14px;line-height:1.65;color:var(--ink);background:#FBF6EE;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:4px;padding:14px 18px}
.entry.ai .body b{font-weight:600}
.note-h{font-family:var(--serif);font-size:16.5px;font-weight:500;color:var(--ink);margin:14px 0 4px}
.note-h:first-child{margin-top:0}
.body ul{margin:4px 0 6px 18px;padding:0}
.body li{margin:2px 0}
.evidence{margin-top:14px;padding-top:10px;border-top:1px dashed var(--line-2);font-family:var(--mono);font-size:11px;color:var(--muted);line-height:1.6}
.evidence b{color:var(--ink-2);font-weight:500}
.draft{margin-top:10px;font-size:11.5px;color:var(--faint);font-style:italic}
.entry.ai.warn .body{background:#FBF1EC;border-left-color:var(--danger);color:var(--ink-2);font-size:13px}
.entry.ai.warn .who{color:var(--danger)}
.bubble-img{max-width:240px;max-height:170px;border-radius:4px;margin-top:8px;display:block;object-fit:cover;border:1px solid var(--line)}
.bubble-file{display:inline-flex;align-items:center;gap:6px;background:var(--paper);border:1px solid var(--line);border-radius:4px;padding:4px 10px;font-family:var(--mono);font-size:11px;color:var(--ink-2);margin-top:8px}
.reviewing{display:flex;align-items:center;gap:12px;margin:10px 6px 20px;font-family:var(--serif);font-style:italic;font-size:14px;color:var(--muted)}
.reviewing .bar{width:70px;height:2px;background:var(--line);position:relative;overflow:hidden;border-radius:2px}
.reviewing .bar::after{content:'';position:absolute;left:-30px;top:0;width:30px;height:2px;background:var(--accent);animation:slide 1.1s ease-in-out infinite}
@keyframes slide{0%{left:-30px}100%{left:70px}}
.empty-chat{padding:36px 30px 10px;text-align:center}
.empty-chat .et{font-family:var(--serif);font-size:26px;font-weight:400;color:var(--ink);margin-bottom:8px}
.empty-chat .es{font-size:14px;color:var(--muted);max-width:420px;line-height:1.65;margin:0 auto 18px}
.inp-lbl{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:12px 2px 4px}
.disc{text-align:left;font-size:11.5px;color:var(--faint);padding:6px 2px;font-style:italic;font-family:var(--serif)}
.modal-err{color:var(--danger);font-size:12.5px;margin:4px 0}
.st-key-confirm_del_btn button{background:var(--danger)!important;border-color:var(--danger)!important}
.st-key-confirm_del_btn button:hover{background:#86291D!important}
.st-key-symsel_open_btn button,[class*="st-key-voice_pop"] button{width:100%}

/* SmartCare unified blue-and-white clinical workspace */
:root{--paper:#F3F8FF;--sheet:#FFFFFF;--ink:#10274D;--ink-2:#405B7D;--muted:#6882A0;--faint:#94A9BF;--line:#E1ECF8;--line-2:#C9DAEE;--accent:#087BD8;--accent-soft:#E9F4FF;--sage:#1785D3;--danger:#B84D57;--pri:var(--ink);--pri-d:#092045;--pri-l:#E9F4FF;--bg:var(--paper);--white:var(--sheet);--border:var(--line);--text:var(--ink);--light:var(--faint);--error:var(--danger);--success:#197AAB;--serif:'DM Sans',sans-serif;--sans:'DM Sans',sans-serif;--mono:'DM Sans',sans-serif}
.stApp{background:linear-gradient(135deg,#F7FBFF 0%,#EFF7FF 100%)!important;color:var(--ink)!important}
.stApp:not(:has(.blue-login-marker)) .block-container{max-width:1440px!important;padding:2.2rem 3rem!important}
.stApp:not(:has(.blue-login-marker)) .dash-h{font-family:var(--sans)!important;font-size:clamp(30px,3.1vw,43px)!important;font-weight:800!important;letter-spacing:-.05em!important}
.stApp:not(:has(.blue-login-marker)) .dash-sec .t{font-family:var(--sans)!important;font-weight:800!important}
.stApp:not(:has(.blue-login-marker)) .dash-date{color:#087BD8!important;font-weight:800!important}
.stApp:not(:has(.blue-login-marker)) .stApp button{border-radius:12px!important}
[data-testid="stSidebar"]{background:#FFFFFF!important;border-right:1px solid #DDEAF8!important}
[data-testid="stSidebar"] .sb-name{font-family:var(--sans)!important;font-weight:800!important;color:#10274D!important;font-size:24px!important;letter-spacing:-.04em!important}
[data-testid="stSidebar"] .sb-tag{font-family:var(--sans)!important;color:#087BD8!important;font-weight:800!important;letter-spacing:.1em!important}
[data-testid="stSidebar"] .sec-lbl,[data-testid="stSidebar"] p,[data-testid="stSidebar"] label{color:#405B7D!important}
[data-testid="stSidebar"] button{color:#244D7B!important;border-color:#D9E8F8!important;border-radius:10px!important}
[data-testid="stSidebar"] button:hover{background:#EAF4FF!important;color:#086CBD!important}
[data-testid="stSidebar"] [data-testid^="stBaseButton-primary"]{background:#087BD8!important;border-color:#087BD8!important;color:#FFFFFF!important}
[data-testid="stSidebar"] [data-testid^="stBaseButton-primary"] p{color:#FFFFFF!important}
[data-testid="stSidebar"] input{background:#F6FAFF!important;color:#10274D!important;border-color:#CBDFF2!important}
[data-testid="stSidebar"] input::placeholder{color:#829AB3!important}
.stApp [data-testid^="stBaseButton-primary"]{background:#087BD8!important;border-color:#087BD8!important;color:#FFFFFF!important}
.stApp [data-testid^="stBaseButton-primary"]:hover{background:#0567B9!important}
.stApp [data-testid^="stBaseButton-primary"] p{color:#FFFFFF!important}
.stApp:not(:has(.blue-login-marker)) [data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#E0ECF8!important}
.stApp:not(:has(.blue-login-marker)) .av{border-radius:10px!important}
.dx-panel{font-family:var(--sans);background:#fff;border:1px solid #DCEAF8;border-radius:18px;padding:28px;margin:12px 0;box-shadow:0 12px 32px rgba(17,49,39,.05)}
.dx-eyebrow{font-size:10px;letter-spacing:.17em;font-weight:700;color:#087BD8;margin-bottom:9px}
.dx-heading{font-family:var(--serif);font-size:28px;color:#123A67;line-height:1.2;margin-bottom:9px}
.dx-heading span{font-family:var(--sans);font-size:11px;font-weight:700;background:#E7F3FF;color:#126FBC;border-radius:50px;padding:6px 11px;vertical-align:middle;margin-left:9px}
.dx-intro{font-size:12px;color:#70837A;margin-bottom:23px}
.dx-card{display:flex;gap:17px;padding:19px 16px;margin:10px 0;border-radius:12px;border:1px solid #DCEAF8;background:#FAFCFF}
.dx-card:first-of-type{border-color:#A6CFF2;background:#F0F8FF}
.dx-number{font-family:var(--serif);font-size:29px;line-height:1;color:#087BD8;min-width:36px}
.dx-overline{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#6882A0;font-weight:700;margin-bottom:5px}
.dx-title{font-family:var(--serif);font-size:19px;color:#143D69;margin-bottom:7px}
.dx-reason{font-size:13px;line-height:1.7;color:#405B7D}
.dx-follow{margin-top:22px;padding:20px 22px;background:#0C4277;border-radius:12px;color:#EFF8FF;font-size:13px;line-height:1.7}
.dx-follow-title{font-family:var(--serif);font-size:18px;color:#FFF; margin-bottom:7px}
.dx-translation{font-size:12px;color:#405B7D;padding:14px 0}
.dx-disclaimer{font-size:10px;color:#7E94AB;letter-spacing:.02em;margin-top:17px}
@media(max-width:760px){.block-container{padding:1.2rem!important}.dx-panel{padding:16px}.dx-heading{font-size:23px}}
</style>
"""

LOGIN_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
header[data-testid="stHeader"]{display:none!important}
.stApp:has(.blue-login-marker){background:radial-gradient(circle at 92% 10%,#91caff 0%,#d9ecff 24%,transparent 52%),linear-gradient(115deg,#fff 0%,#f7fbff 45%,#ddecff 100%)!important;color:#10274d!important;font-family:'DM Sans',sans-serif!important}
.stApp:has(.blue-login-marker) .block-container{max-width:1440px!important;padding:2.2rem 4.2rem 1.5rem!important}
.stApp:has(.blue-login-marker) [data-testid="stHorizontalBlock"]{align-items:stretch;gap:4.5rem!important}
.stApp:has(.blue-login-marker) [data-testid="stColumn"]{background:transparent!important;border:none!important;padding:0!important}
.blue-login-marker{height:0}
.blue-brand{display:flex;align-items:center;gap:14px;font-size:28px;font-weight:800;line-height:1.04;letter-spacing:-.055em;color:#10234a;margin-bottom:64px}
.blue-brand-icon{width:62px;height:62px;border-radius:19px;background:linear-gradient(145deg,#41b5ff,#0967c5);display:flex;align-items:center;justify-content:center;box-shadow:0 12px 26px #2779d42c}
.blue-brand-icon svg{width:48px;height:48px}
.blue-eyebrow{font-size:11px;font-weight:800;letter-spacing:.22em;color:#2781d0;margin-bottom:16px;text-transform:uppercase}
.blue-title{font-size:clamp(44px,4.4vw,72px);line-height:1.05;font-weight:800;letter-spacing:-.065em;color:#0b2248;margin:0 0 22px}
.blue-title span{color:#0878d7}
.blue-desc{font-size:17px;line-height:1.65;color:#3f5778;max-width:530px;margin:0 0 24px}
.blue-feature{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 10px}
.blue-feature span{font-size:12px;font-weight:700;color:#24649d;background:#e8f4ff;border:1px solid #cfe6ff;padding:9px 13px;border-radius:30px}
.blue-illustration{margin-top:4px;width:100%;max-width:690px;display:block;mix-blend-mode:multiply;mask-image:linear-gradient(to bottom,black 0%,black 84%,transparent 100%)}
.blue-card-top{height:65px}
.blue-card-heading{text-align:center;font-size:34px;font-weight:800;letter-spacing:-.04em;color:#10234a;margin:14px 0 4px}
.blue-card-sub{text-align:center;color:#58718e;font-size:14px;margin-bottom:26px}
.blue-card-icon{width:75px;height:75px;margin:auto;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#e0f0ff;color:#0c77d3;font-size:35px}
.blue-card-bottom{text-align:center;margin-top:20px;color:#177cda;font-size:22px;letter-spacing:.18em}
.stApp:has(.blue-login-marker) [data-testid="stForm"]{border:none!important;padding:0!important;background:transparent!important}
.stApp:has(.blue-login-marker) .stTextInput label p{font-size:13px!important;font-weight:700!important;color:#304d73!important}
.stApp:has(.blue-login-marker) .stTextInput input{background:#fff!important;border:1px solid #c9d9ec!important;border-radius:12px!important;min-height:52px!important;color:#10274d!important;font-size:15px!important}
.stApp:has(.blue-login-marker) .stTextInput input:focus{border-color:#218ce3!important;box-shadow:0 0 0 3px #228ce323!important}
.stApp:has(.blue-login-marker) [data-testid^="stBaseButton-primary"]{background:#087bd8!important;border-color:#087bd8!important;border-radius:12px!important;min-height:54px!important;font-weight:800!important;color:#fff!important}
.stApp:has(.blue-login-marker) [data-testid^="stBaseButton-primary"]:hover{background:#0566b6!important}
.blue-demo{font-size:11px;text-align:center;color:#6e829a;margin-top:16px}
.blue-demo b{color:#225f9e}
.blue-error{font-size:13px;color:#ba3434;margin:12px 0}
/* The form column is a Streamlit container so it stays interactive. */
.stApp:has(.blue-login-marker) [data-testid="stColumn"]:nth-child(2)>div{background:#ffffffeb;border:1px solid #ffffff;border-radius:34px;padding:38px 38px 24px;box-shadow:0 22px 80px #1b69b52a;max-width:520px;margin:58px auto 0;backdrop-filter:blur(12px)}
@media(max-width:900px){.stApp:has(.blue-login-marker) .block-container{padding:24px!important}.stApp:has(.blue-login-marker) [data-testid="stHorizontalBlock"]{gap:1.5rem!important}.blue-brand{margin-bottom:26px}.blue-illustration{max-width:480px}.stApp:has(.blue-login-marker) [data-testid="stColumn"]:nth-child(2)>div{margin:10px auto;padding:24px}.blue-title{font-size:42px}}
</style>
"""

TYPING_HTML = """
<div class="reviewing"><div class="bar"></div><span>Reviewing similar cases…</span></div>
"""
