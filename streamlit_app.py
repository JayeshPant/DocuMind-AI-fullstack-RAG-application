import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Load local environment if present
root_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv(dotenv_path=root_dir / "backend" / ".env")

# Set Page Config
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e1b4b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #475569;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .detected-box {
        background-color: #eef2ff;
        border-left: 4px solid #4f46e5;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .evidence-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #334155;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# 1. API Key Configuration
api_key = os.getenv("NVIDIA_API_KEY", "")
if not api_key:
    try:
        api_key = st.secrets["NVIDIA_API_KEY"]
    except Exception:
        api_key = ""

# Sidebar for settings & document management
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bot.png", width=64)
    st.title("DocuMind AI")
    st.caption("Your Intelligent PDF Question Answering Assistant")
    st.markdown("---")

    if not api_key:
        st.warning("⚠️ NVIDIA API Key not detected.")
        user_key = st.text_input("Enter NVIDIA API Key:", type="password", placeholder="nvapi-...")
        if user_key:
            api_key = user_key
            os.environ["NVIDIA_API_KEY"] = user_key
    else:
        st.success("✅ NVIDIA Key configured")

    st.markdown("### 📄 Document Selector")
    uploaded_file = st.file_uploader("Upload a PDF document:", type=["pdf"])

    stats_default_path = root_dir / "document_loader" / "STATS.pdf"
    has_default_pdf = stats_default_path.exists()

    if not uploaded_file and has_default_pdf:
        st.info("📌 Using preloaded **STATS.pdf**")

# App Header
st.markdown('<div class="main-header">DocuMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Retrieval-Augmented Generation powered by LangChain, FastEmbed, Qdrant & NVIDIA Nemotron</div>', unsafe_allow_html=True)

if not api_key:
    st.info("👋 Welcome! Please enter your free **NVIDIA API Key** in the sidebar to begin. (Get a key at [build.nvidia.com](https://build.nvidia.com/)).")
    st.stop()

# Import backend RAG services
from backend.app.config import settings
from backend.app.services.pdf_service import pdf_service
from backend.app.services.rag_service import rag_service
from backend.app.services.question_number_service import question_number_service

# Ensure settings uses the active key
settings.NVIDIA_API_KEY = api_key
rag_service.refresh_key(api_key)

# 2. Process and Index Document
@st.cache_resource(show_spinner="Indexing document into vector store...")
def load_and_index_pdf(file_bytes: bytes, filename: str, doc_id: str):
    doc_id_clean, file_path = pdf_service.save_uploaded_file(file_bytes, filename)
    pages, chunks = pdf_service.load_and_split(file_path, doc_id, filename)
    rag_service.index_document(doc_id, chunks)
    return pages, chunks, filename

current_doc_id = "doc_default"
current_doc_name = "STATS.pdf"
pages = []

if uploaded_file is not None:
    current_doc_name = uploaded_file.name
    current_doc_id = f"doc_{uploaded_file.name.replace(' ', '_')}"
    file_bytes = uploaded_file.read()
    with st.spinner(f"Indexing '{current_doc_name}' with FastEmbed & Qdrant..."):
        pages, chunks, _ = load_and_index_pdf(file_bytes, current_doc_name, current_doc_id)
elif has_default_pdf:
    with open(stats_default_path, "rb") as f:
        file_bytes = f.read()
    pages, chunks, _ = load_and_index_pdf(file_bytes, "STATS.pdf", current_doc_id)
else:
    st.warning("Please upload a PDF document in the sidebar to begin.")
    st.stop()

# Document Info Bar
col1, col2, col3 = st.columns(3)
col1.metric("Active Document", current_doc_name)
col2.metric("Total Pages", len(pages))
col3.metric("Vector Chunks", len(chunks) if 'chunks' in locals() else 0)

st.markdown("---")

# 3. Two Modes: Ask by Number vs Free Text
tab1, tab2 = st.tabs(["🔢 Mode 1: Ask by Question Number", "💬 Mode 2: Ask Anything (Free Text)"])

# Mode 1: Ask by Question Number
with tab1:
    st.markdown("#### Enter a Question Number from the Document")
    st.caption("DocuMind will locate the exact question in the PDF (e.g. Q1., Question 1, 1.), extract its full text, and generate a grounded answer.")

    c1, c2 = st.columns([1, 3])
    with c1:
        q_num = st.number_input("Question Number:", min_value=1, step=1, value=1)
    with c2:
        st.write("")
        st.write("")
        btn_number = st.button("🔍 Find and Answer Question", type="primary", use_container_width=True)

    if btn_number:
        with st.spinner(f"Locating Question #{q_num} in {current_doc_name}..."):
            found, detected_q, page_num, not_found_msg = question_number_service.find_question_by_number(pages, int(q_num))

            if not found or not detected_q:
                st.error(not_found_msg or f"Question number {q_num} was not found in {current_doc_name}.")
            else:
                st.markdown(f"""
                <div class="detected-box">
                    <span style="font-size: 0.75rem; font-weight: 700; color: #4338ca; text-transform: uppercase;">Detected Question (Page {page_num})</span>
                    <div style="font-weight: 600; color: #1e1b4b; font-size: 1rem; margin-top: 4px;">{detected_q}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Generating answer from NVIDIA Nemotron..."):
                    try:
                        answer, retrieved_docs = rag_service.query(current_doc_id, f"Question {q_num}: {detected_q}")
                        st.markdown("### 🎓 Academic Tutor Answer")
                        st.markdown(answer)

                        if retrieved_docs:
                            with st.expander(f"📚 Retrieved Document Evidence ({len(retrieved_docs)} chunks)"):
                                for i, doc in enumerate(retrieved_docs, start=1):
                                    page_idx = doc.metadata.get("page", 1)
                                    st.markdown(f"**Chunk {i} (Page {page_idx}):**")
                                    st.markdown(f'<div class="evidence-box">"{doc.page_content.strip()}"</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error during LLM generation: {e}")

# Mode 2: Free-text question
with tab2:
    st.markdown("#### Ask Any Question About the Document")
    free_question = st.text_area("Your Question:", placeholder="e.g. What are the normal equations for fitting a straight line using the principle of least squares?")
    btn_free = st.button("🚀 Ask Question", type="primary")

    if btn_free and free_question.strip():
        with st.spinner("Retrieving context and generating answer from NVIDIA Nemotron..."):
            try:
                answer, retrieved_docs = rag_service.query(current_doc_id, free_question.strip())
                st.markdown("### 🎓 Academic Tutor Answer")
                st.markdown(answer)

                if retrieved_docs:
                    with st.expander(f"📚 Retrieved Document Evidence ({len(retrieved_docs)} chunks)"):
                        for i, doc in enumerate(retrieved_docs, start=1):
                            page_idx = doc.metadata.get("page", 1)
                            st.markdown(f"**Chunk {i} (Page {page_idx}):**")
                            st.markdown(f'<div class="evidence-box">"{doc.page_content.strip()}"</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error during LLM generation: {e}")
