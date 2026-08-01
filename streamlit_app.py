import html
import importlib
from pathlib import Path

import streamlit as st

from app.delete_document import delete_document
from app.pipeline import process_pdf
from app.retrieval import retrieve_chunks
from app.llm import generate_answer

st.set_page_config(page_title="DocPilot AI", layout="wide")

# ---------------------------------------------------------------------------
# GLOBAL THEME CSS
# ---------------------------------------------------------------------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ------- App background with soft glows ------- */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(700px 420px at 12% -6%, rgba(99, 102, 241, 0.16), transparent 60%),
        radial-gradient(760px 520px at 100% -4%, rgba(6, 182, 212, 0.12), transparent 60%),
        radial-gradient(900px 700px at 50% 118%, rgba(139, 92, 246, 0.10), transparent 60%),
        #0B0F1A;
    color: #E6EAF5;
}

/* ------- Hide default streamlit chrome ------- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent; height: 0; min-height: 0;}
[data-testid="stToolbar"], [data-testid="stDecoration"] {display: none;}

/* ------- Main column width ------- */
.block-container {
    max-width: 960px;
    margin: 0 auto;
    padding-top: 1.4rem;
    padding-bottom: 2.5rem;
}

/* ------- Scrollbar ------- */
::-webkit-scrollbar {width: 8px; height: 8px;}
::-webkit-scrollbar-track {background: transparent;}
::-webkit-scrollbar-thumb {background: rgba(255,255,255,0.12); border-radius: 8px;}
::-webkit-scrollbar-thumb:hover {background: rgba(255,255,255,0.22);}

/* ------- Sidebar ------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101628 0%, #0B0F1A 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] > div:first-child {padding-top: 1rem;}

.side-brand {display: flex; align-items: center; gap: 12px; padding: 0.2rem 0 0.9rem;}
.side-logo svg {display: block; border-radius: 12px; box-shadow: 0 4px 14px rgba(99,102,241,0.35);}
.side-name {font-family: 'Sora', sans-serif; font-size: 1.3rem; font-weight: 700; color: #fff;}
.side-sub {color: #6B7280; font-size: 0.72rem;}

.side-section-label {
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.14em;
    color: #6B7280; font-weight: 700; margin: 1.3rem 0 0.55rem;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    transition: border-color .2s ease;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(139,92,246,0.45);
}

/* ------- File uploader ------- */
[data-testid="stFileUploader"] section {
    border: 1px dashed rgba(255,255,255,0.22);
    border-radius: 14px;
    background: rgba(255,255,255,0.03);
    transition: all .2s ease;
}
[data-testid="stFileUploader"] section:hover {border-color: #8B5CF6; background: rgba(139,92,246,0.06);}
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {min-height: 110px;}

/* ------- Buttons ------- */
.stButton > button {
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.045);
    color: #E6EAF5;
    font-weight: 500;
    transition: all .2s ease;
}
.stButton > button:hover {
    border-color: rgba(124,108,240,0.65);
    background: rgba(124,108,240,0.14);
    color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.3);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    border: none;
    color: #fff;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    box-shadow: 0 8px 22px rgba(124,108,240,0.4);
}

/* ------- Doc card ------- */
.doc-card .doc-head {display: flex; align-items: center; gap: 10px;}
.doc-ic {font-size: 1.35rem;}
.doc-name {color: #E6EAF5; font-weight: 600; font-size: 0.85rem; word-break: break-word; line-height: 1.35;}
.doc-sub {color: #6B7280; font-size: 0.72rem; margin-top: 1px;}
.doc-ready {display: inline-flex; align-items: center; gap: 6px; color: #34D399; font-size: 0.72rem; font-weight: 500;}
.ready-dot {width: 7px; height: 7px; border-radius: 50%; background: #34D399; box-shadow: 0 0 7px rgba(52,211,153,0.9);}

.empty-docs {
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(255,255,255,0.14);
    border-radius: 12px; padding: 1rem; text-align: center;
    color: #6B7280; font-size: 0.8rem; line-height: 1.6;
}

/* ------- Delete confirmation ------- */
.confirm-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.32);
    border-radius: 12px; padding: 0.9rem; margin: 0.7rem 0;
    animation: fadeUp .3s ease both;
}
.confirm-title {color: #FCA5A5; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;}
.confirm-text {color: #F87171; font-size: 0.78rem; line-height: 1.55;}

/* ------- Stats ------- */
.stat-grid {display: grid; grid-template-columns: 1fr 1fr; gap: 10px;}
.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 0.85rem 0.5rem; text-align: center;
    transition: border-color .2s ease;
}
.stat-card:hover {border-color: rgba(139,92,246,0.4);}
.stat-value {font-family: 'Sora', sans-serif; font-size: 1.45rem; font-weight: 700; color: #fff;}
.stat-label {color: #6B7280; font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 2px;}

/* ------- Header ------- */
.app-header {display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 0.2rem 0 1rem;}
.brand-lockup {display: flex; align-items: center; gap: 14px;}
.brand-logo svg {display: block; border-radius: 14px; box-shadow: 0 6px 20px rgba(99,102,241,0.4);}
.brand-name {font-family: 'Sora', sans-serif; font-size: 1.65rem; font-weight: 700; color: #fff; line-height: 1.1;}
.brand-ai {
    background: linear-gradient(90deg, #8B5CF6, #06B6D4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-sub {font-size: 0.8rem; color: #8A93A6; margin-top: 2px;}

.header-divider {
    height: 1px; border: none; margin: 0 0 1.2rem;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.55), rgba(6,182,212,0.55), transparent);
}

/* ------- Welcome / Hero ------- */
.welcome-wrap {text-align: center; padding: 2rem 0.5rem 0.5rem;}
.welcome-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 16px; border-radius: 999px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.3);
    color: #A78BFA; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em;
}
.welcome-title {
    font-family: 'Sora', sans-serif; font-size: 2.9rem; font-weight: 800;
    color: #fff; line-height: 1.18; margin: 1.1rem 0 0.7rem;
}
.gradient-text {
    background: linear-gradient(90deg, #818CF8, #C084FC, #22D3EE);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.welcome-sub {color: #8A93A6; font-size: 1.02rem; max-width: 620px; margin: 0 auto 2.1rem; line-height: 1.65;}
.feature-grid {display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; max-width: 980px; margin: 0 auto;}
@media (max-width: 900px) {.feature-grid {grid-template-columns: repeat(2, 1fr);}}
.feature-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1.1rem 1rem; text-align: left;
    transition: all .25s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(139,92,246,0.5);
    background: rgba(139,92,246,0.07);
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
}
.feature-icon {font-size: 1.55rem; margin-bottom: 0.55rem;}
.feature-title {font-family: 'Sora', sans-serif; font-weight: 600; color: #fff; margin-bottom: 0.3rem; font-size: 0.95rem;}
.feature-desc {color: #8A93A6; font-size: 0.8rem; line-height: 1.55;}
.suggest-title {
    text-align: center; color: #8A93A6; font-size: 0.78rem; letter-spacing: 0.14em;
    text-transform: uppercase; font-weight: 600; margin: 2.2rem 0 0.85rem;
}

/* ------- Chat messages ------- */
@keyframes fadeUp {from {opacity: 0; transform: translateY(8px);} to {opacity: 1; transform: translateY(0);}}
[data-testid="stChatMessage"] {
    display: flex !important;
    align-items: flex-start;
    gap: 12px;
    padding: 4px 0;
    animation: fadeUp .35s ease both;
    margin-bottom: 0.4rem;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {flex-direction: row-reverse;}

[data-testid="stChatMessageContent"] {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 18px 18px 18px;
    padding: 12px 18px;
    max-width: 84%;
    font-size: 0.95rem;
    line-height: 1.65;
    color: #E6EAF5;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, rgba(99,102,241,0.20), rgba(139,92,246,0.24));
    border: 1px solid rgba(139,92,246,0.38);
    border-radius: 18px 4px 18px 18px;
}
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] p:last-child {margin-bottom: 0;}

[data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] {
    border-radius: 50% !important;
    display: flex !important;
    align-items: center;
    justify-content: center;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #6366F1, #06B6D4) !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.16);
}
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #22D3EE, #3B82F6) !important;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.16);
}

/* ------- Chat input ------- */
[data-testid="stChatInput"] {
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 18px;
    background: rgba(255,255,255,0.04);
    padding: 4px 6px;
    transition: all .2s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #8B5CF6;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.16);
}
[data-testid="stChatInput"] textarea {background: transparent !important; color: #E6EAF5 !important;}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    border-radius: 12px !important;
    color: #fff !important;
}

/* ------- Sources ------- */
.sources-label {
    font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase;
    color: #8A93A6; font-weight: 700; margin: 1rem 0 0.55rem;
}
.source-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 12px; padding: 0.7rem 0.9rem; margin-bottom: 0.5rem;
    transition: all .2s ease;
}
.source-card:hover {border-color: rgba(139,92,246,0.5); background: rgba(139,92,246,0.06);}
.source-top {display: flex; align-items: center; gap: 8px; flex-wrap: wrap;}
.source-file {font-weight: 600; color: #E6EAF5; font-size: 0.84rem; word-break: break-word;}
.source-page {
    background: rgba(99,102,241,0.16); color: #A5B4FC;
    border-radius: 6px; padding: 2px 8px; font-size: 0.7rem; font-weight: 600;
}
.source-score {margin-left: auto; color: #34D399; font-size: 0.75rem; font-weight: 600; white-space: nowrap;}
.source-snippet {color: #8A93A6; font-size: 0.78rem; margin-top: 0.42rem; line-height: 1.55;}

/* ------- Typing indicator ------- */
.typing-bubble {
    display: inline-flex; align-items: center; gap: 11px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 4px 18px 18px 18px;
    padding: 15px 20px;
    animation: fadeUp .25s ease both;
}
.typing-dots {display: flex; gap: 5px;}
.typing-dots span {
    width: 8px; height: 8px; border-radius: 50%; background: #8B5CF6;
    animation: blink 1.4s infinite both;
}
.typing-dots span:nth-child(2) {animation-delay: 0.2s;}
.typing-dots span:nth-child(3) {animation-delay: 0.4s;}
@keyframes blink {0%, 80%, 100% {opacity: 0.3; transform: translateY(0);} 40% {opacity: 1; transform: translateY(-4px);}}
.typing-text {color: #8A93A6; font-size: 0.85rem;}

/* ------- Expander ------- */
[data-testid="stExpander"] details {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
}
[data-testid="stExpander"] summary {font-weight: 600;}

/* ------- Misc ------- */
.stCaption, [data-testid="stCaptionContainer"] p {color: #6B7280;}
[data-testid="stToast"] {background: #131A2B !important;}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CONSTANTS / ASSETS
# ---------------------------------------------------------------------------
LOGO_SVG = """
<svg width="46" height="46" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="dpGrad" x1="0" y1="0" x2="48" y2="48">
      <stop stop-color="#6366F1"/>
      <stop offset="0.5" stop-color="#8B5CF6"/>
      <stop offset="1" stop-color="#06B6D4"/>
    </linearGradient>
  </defs>
  <rect x="1.5" y="1.5" width="45" height="45" rx="13" fill="url(#dpGrad)"/>
  <path d="M15 13h12l6 6v16a2 2 0 0 1-2 2H15a2 2 0 0 1-2-2V15a2 2 0 0 1 2-2z" fill="#fff" fill-opacity="0.95"/>
  <path d="M27 13v6h6" stroke="#6366F1" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="M18 27h12M18 31h8" stroke="#6366F1" stroke-width="2.2" stroke-linecap="round"/>
  <circle cx="34.5" cy="13.5" r="3.2" fill="#22D3EE"/>
</svg>
"""

HEADER_HTML = f"""
<div class="app-header">
  <div class="brand-lockup">
    <div class="brand-logo">{LOGO_SVG}</div>
    <div>
      <div class="brand-name">DocPilot <span class="brand-ai">AI</span></div>
      <div class="brand-sub">Document Intelligence Copilot</div>
    </div>
  </div>
</div>
"""

SIDEBAR_BRAND_HTML = f"""
<div class="side-brand">
  <div class="side-logo">{LOGO_SVG}</div>
  <div>
    <div class="side-name">DocPilot</div>
    <div class="side-sub">RAG Workspace</div>
  </div>
</div>
"""

TYPING_HTML = """
<div class="typing-bubble">
  <div class="typing-dots"><span></span><span></span><span></span></div>
  <span class="typing-text">DocPilot is thinking…</span>
</div>
"""

WELCOME_HTML = """
<div class="welcome-wrap">
  <h1 class="welcome-title">Chat with your<br><span class="gradient-text">PDF documents</span></h1>
  <p class="welcome-sub">
    Upload a PDF, ask questions, and get precise answers with source citations —
    all powered by semantic search and Groq's Llama 3.3.
  </p>
  <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon"></div>
      <div class="feature-title">Instant Upload</div>
      <div class="feature-desc">Drop any PDF — it's parsed, chunked &amp; indexed automatically.</div>
    </div>
        <div class="feature-card">
            <div class="feature-icon"></div>
      <div class="feature-title">Semantic Search</div>
      <div class="feature-desc">Questions match meaning, not just keywords.</div>
    </div>
        <div class="feature-card">
            <div class="feature-icon"></div>
      <div class="feature-title">Fast Answers</div>
      <div class="feature-desc">Groq Llama 3.3 delivers responses in seconds.</div>
    </div>
        <div class="feature-card">
            <div class="feature-icon"></div>
      <div class="feature-title">Source Citations</div>
      <div class="feature-desc">Every answer links back to the exact page.</div>
    </div>
  </div>
</div>
"""

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "data" / "pdfs"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "delete_target" not in st.session_state:
    st.session_state.delete_target = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=3600)
def get_pdf_pages(path_str, mtime_ns):
    """Return the page count of a PDF (cached by path + mtime)."""
    try:
        fitz = importlib.import_module("pymupdf")
        doc = fitz.open(path_str)
        pages = len(doc)
        doc.close()
        return pages
    except Exception:
        return None


def fmt_size(size_bytes):
    kb = size_bytes / 1024
    if kb < 1024:
        return f"{kb:.0f} KB"
    return f"{kb / 1024:.1f} MB"


def render_sources(sources):
    st.markdown('<div class="sources-label">Sources</div>', unsafe_allow_html=True)
    for src in sources:
        doc = html.escape(src["document_name"])
        page = src["page_number"]
        score = src.get("score", 0.0)
        raw_snippet = src.get("chunk", "")
        snippet = html.escape(raw_snippet)[:170]
        suffix = "…" if len(raw_snippet) > 170 else ""
        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-top">
                    <span class="source-file">{doc}</span>
                    <span class="source-page">Page {page}</span>
                    <span class="source-score">{score:.0%} match</span>
                </div>
                <div class="source-snippet">{snippet}{suffix}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_message(msg):
    role = msg["role"]
    avatar = None
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])
        if role == "assistant" and msg.get("sources"):
            render_sources(msg["sources"])


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(SIDEBAR_BRAND_HTML, unsafe_allow_html=True)

    st.markdown('<div class="side-section-label">Upload PDF</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload a PDF document", type=["pdf"], label_visibility="collapsed"
    )

    if uploaded_file:
        save_path = UPLOAD_FOLDER / uploaded_file.name
        if st.button("Upload & Process", type="primary", use_container_width=True):
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.spinner("Parsing, chunking & embedding…"):
                process_pdf(save_path)
            st.toast("PDF processed successfully!")
            st.rerun()

    st.markdown('<div class="side-section-label">Documents</div>', unsafe_allow_html=True)
    pdf_files = sorted(UPLOAD_FOLDER.glob("*.pdf"))

    if pdf_files:
        for pdf in pdf_files:
            size = pdf.stat().st_size
            pages = get_pdf_pages(str(pdf), pdf.stat().st_mtime_ns)
            name = html.escape(pdf.name)
            pages_str = f" • {pages} pages" if pages else ""
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="doc-card">
                        <div class="doc-head">
                            <span class="doc-ic"></span>
                            <div>
                                <div class="doc-name">{name}</div>
                                <div class="doc-sub">{fmt_size(size)}{pages_str}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(
                        '<span class="doc-ready"><span class="ready-dot"></span> Indexed</span>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button(
                        "🗑", key=f"del_{pdf.name}", help="Delete document",
                        use_container_width=True,
                    ):
                        st.session_state.delete_target = pdf.name
                        st.rerun()
    else:
        st.markdown(
            '<div class="empty-docs">No PDFs uploaded yet.<br>Upload your first document above.</div>',
            unsafe_allow_html=True,
        )

    # Delete confirmation
    if st.session_state.delete_target:
        target = html.escape(st.session_state.delete_target)
        st.markdown(
            f"""
            <div class="confirm-box">
                <div class="confirm-title">Delete document?</div>
                <div class="confirm-text">
                    This will permanently remove <b>{target}</b> and all of its embeddings.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        a, b = st.columns(2)
        with a:
            if st.button("Cancel", use_container_width=True):
                st.session_state.delete_target = None
                st.rerun()
        with b:
            if st.button("Delete", type="primary", use_container_width=True):
                delete_document(st.session_state.delete_target)
                st.toast(f"{st.session_state.delete_target} deleted")
                st.session_state.delete_target = None
                st.rerun()

    st.markdown('<div class="side-section-label">Statistics</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="stat-grid">
            <div class="stat-card"><div class="stat-value">{len(pdf_files)}</div><div class="stat-label">Documents</div></div>
            <div class="stat-card"><div class="stat-value">{len(st.session_state.messages)}</div><div class="stat-label">Messages</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-section-label">Actions</div>', unsafe_allow_html=True)
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("DocPilot AI • v1.0 • Powered by Groq")

# ---------------------------------------------------------------------------
# MAIN AREA
# ---------------------------------------------------------------------------
st.markdown(HEADER_HTML, unsafe_allow_html=True)
st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)

query = None

# ---- Chat input ----
chat_input = st.chat_input("Ask anything about your documents…")
if chat_input:
    query = chat_input

# Suggested-question clicks become a pending query so the
# welcome screen transitions cleanly into the chat view.
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

if not st.session_state.messages and not query:
    # ---- Welcome / empty state ----
    st.markdown(WELCOME_HTML, unsafe_allow_html=True)
    st.markdown('<div class="suggest-title">Try asking</div>', unsafe_allow_html=True)

    suggestions = [
        "What is this document about?",
        "Summarize the key points",
        "What are the main sections?",
        "List the most important takeaways",
    ]
    cols = st.columns(2)
    for i, q in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(q, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_query = q
                st.rerun()
elif query:
    # ---- Chat history ----
    for msg in st.session_state.messages:
        render_message(msg)

# ---- Process query ----
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    render_message(st.session_state.messages[-1])

    typing = st.empty()
    typing.markdown(TYPING_HTML, unsafe_allow_html=True)

    matches = []
    answer = "Something went wrong while querying your documents. Please try again."
    try:
        matches = retrieve_chunks(query=query, top_k=3)
        answer = generate_answer(query, matches, include_sources=False)
    except Exception as exc:
        answer = f"An error occurred: {exc}"
    finally:
        typing.empty()

    sources = [
        {
            "document_name": m["document_name"],
            "page_number": m["page_number"],
            "score": m.get("score", 0.0),
            "chunk": m["chunk"],
        }
        for m in matches
    ]

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
    render_message(st.session_state.messages[-1])

