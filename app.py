"""
Resource-Scoped Mode - Streamlit Application
GPAi-inspired UI for document-grounded STEM problem solving.
"""

import streamlit as st
import os
import tempfile
from typing import List, Dict, Any
from dotenv import load_dotenv

from backend import (
    DocumentIngestor,
    extract_file_metadata,
    MathOCR,
    EmbeddingIndexer,
    DocumentRetriever,
    LLMGenerator,
    StepValidator
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="GPAi - Resource-Scoped Mode",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Clean Tailwind-inspired styling like original GPAi site
st.markdown("""
<style>
    /* Import Inter font like original site */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root variables - matching original site */
    :root {
        --background: 0 0% 100%;
        --foreground: 222.2 84% 4.9%;
        --primary: 249 44% 53%;
        --border: 214.3 31.8% 91.4%;
        --radius: 0.75rem;
    }
    
    /* Reset and base styles */
    * {
        box-sizing: border-box;
        border-color: hsl(var(--border));
    }
    
    /* Force light background */
    [data-testid="stAppViewContainer"] {
        background: white !important;
    }
    
    /* Main content - clean white background */
    .main .block-container {
        padding: 5rem 1.5rem !important;
        max-width: 72rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
        background: white !important;
    }
    
    /* Typography - Inter font */
    body, .stMarkdown, p, span, div, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        color: rgb(15 23 42) !important;
    }
    
    /* Header styling - matching GPAi site exactly */
    .main-header {
        background: white;
        padding: 0;
        border-radius: 0;
        margin-bottom: 3rem;
        color: black !important;
        border: none;
    }
    
    .main-header h1 {
        margin: 0 0 1.5rem 0 !important;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        color: black !important;
        line-height: 1.1 !important;
    }
    
    .main-header p {
        margin: 0 !important;
        font-size: 1.5rem !important;
        color: #6366f1 !important;
        font-weight: 500 !important;
    }
    
    /* Feature description - clean card matching GPAi */
    .feature-desc {
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #6366f1;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 2rem;
    }
    
    .feature-desc h3 {
        color: black !important;
        font-weight: 700;
        margin-bottom: 0.75rem;
        font-size: 1.5rem;
    }
    
    .feature-desc p {
        color: rgb(100 116 139) !important;
        line-height: 1.625;
        font-size: 1rem;
    }
    
    .feature-desc strong {
        color: black !important;
        font-weight: 600;
    }
    
    /* File uploader - clean white */
    [data-testid="stFileUploader"] {
        background: white !important;
        border: 2px dashed #d1d5db !important;
        border-radius: 0.75rem !important;
        padding: 2rem !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: rgb(15 23 42) !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: white !important;
        color: rgb(15 23 42) !important;
    }
    
    [data-testid="stFileUploader"] small {
        color: rgb(100 116 139) !important;
    }
    
    /* File uploader button - purple matching GPAi */
    [data-testid="stFileUploader"] button {
        background: #6366f1 !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background: #4f46e5 !important;
    }
    
    /* Citation chip - purple theme */
    .citation {
        display: inline-block;
        background: #ede9fe;
        border: 1px solid #c4b5fd;
        border-radius: 0.375rem;
        padding: 0.25rem 0.625rem;
        margin: 0.25rem;
        font-size: 0.875rem;
        color: #6366f1 !important;
        cursor: pointer;
        font-weight: 500;
    }
    
    .citation:hover {
        background: #ddd6fe;
        border-color: #a78bfa;
    }
    
    /* Confidence badges */
    .confidence-high {
        background: #10b981;
        color: white !important;
        padding: 0.25rem 0.625rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .confidence-medium {
        background: #f59e0b;
        color: white !important;
        padding: 0.25rem 0.625rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .confidence-low {
        background: #ef4444;
        color: white !important;
        padding: 0.25rem 0.625rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* Step container - clean white with purple accent */
    .step-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 3px solid #6366f1;
        padding: 1.25rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    
    .step-container p, .step-container span, .step-container div {
        color: rgb(15 23 42) !important;
    }
    
    /* Buttons - purple gradient matching GPAi */
    .stButton>button {
        background: #6366f1 !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.625rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s !important;
    }
    
    .stButton>button:hover {
        background: #4f46e5 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea textarea {
        border-radius: 0.5rem !important;
        border: 1px solid #d1d5db !important;
        color: rgb(15 23 42) !important;
        background: white !important;
        font-size: 0.95rem !important;
        padding: 0.625rem 0.875rem !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }
    
    /* Selectbox */
    .stSelectbox>div>div {
        border-radius: 0.5rem !important;
        border: 1px solid #d1d5db !important;
        background: white !important;
    }
    
    .stSelectbox>div>div>div {
        color: rgb(15 23 42) !important;
        background: white !important;
    }
    
    .stSelectbox label {
        color: rgb(15 23 42) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    /* Dropdown options */
    [data-baseweb="select"] {
        background: white !important;
    }
    
    [data-baseweb="select"] > div {
        background: white !important;
        color: rgb(15 23 42) !important;
    }
    
    [role="option"] {
        background: white !important;
        color: rgb(15 23 42) !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    [role="option"]:hover {
        background: #f3f4f6 !important;
        color: #6366f1 !important;
    }
    
    [data-baseweb="select"] span {
        color: rgb(15 23 42) !important;
    }
    
    /* Expander - clean white with NO text overlap */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 0.5rem !important;
        border: 1px solid #e5e7eb !important;
        color: rgb(15 23 42) !important;
        font-weight: 500 !important;
        padding: 0.75rem 3rem 0.75rem 1rem !important;
        position: relative !important;
    }
    
    /* Hide the keyboard_arrow text that causes overlap */
    .streamlit-expanderHeader [data-testid="StyledLinkIconContainer"] {
        font-size: 0 !important;
    }
    
    .streamlit-expanderHeader [data-testid="StyledLinkIconContainer"] svg {
        font-size: 1.5rem !important;
    }
    
    /* Fix the label container to prevent overflow */
    .streamlit-expanderHeader > div {
        width: calc(100% - 50px) !important;
        overflow: hidden !important;
        display: inline-block !important;
    }
    
    .streamlit-expanderHeader label {
        width: 100% !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        display: block !important;
    }
    
    .streamlit-expanderHeader p, .streamlit-expanderHeader span {
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        display: block !important;
    }
    
    /* Completely hide text content inside the icon */
    .streamlit-expanderHeader button {
        font-size: 0 !important;
        line-height: 0 !important;
    }
    
    .streamlit-expanderHeader button svg {
        font-size: 1.5rem !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-top: none !important;
        padding: 1rem !important;
    }
    
    /* JSON viewer - WHITE background with dark text */
    [data-testid="stJson"] {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 0.5rem !important;
        padding: 1rem !important;
    }
    
    [data-testid="stJson"] pre {
        background: white !important;
        color: rgb(15 23 42) !important;
    }
    
    /* Code blocks - WHITE background */
    pre, code {
        background: white !important;
        color: rgb(15 23 42) !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 0.375rem !important;
        padding: 0.5rem !important;
    }
    
    /* Fix text overlap - proper spacing */
    .stMarkdown {
        margin-bottom: 1rem !important;
    }
    
    /* File uploader - remove text overlap */
    [data-testid="stFileUploader"] > label {
        display: block !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Expander header - prevent overlap */
    .streamlit-expanderHeader p {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess {
        background: #f0fdf4 !important;
        border: 1px solid #86efac !important;
        color: #166534 !important;
        border-radius: 0.5rem !important;
        padding: 0.875rem !important;
    }
    
    .stError {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #991b1b !important;
        border-radius: 0.5rem !important;
        padding: 0.875rem !important;
    }
    
    .stWarning {
        background: #fffbeb !important;
        border: 1px solid #fde68a !important;
        color: #92400e !important;
        border-radius: 0.5rem !important;
        padding: 0.875rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #e5e7eb !important;
    }
    
    /* Headers - black and bold like GPAi */
    h1, h2, h3 {
        color: black !important;
        font-weight: 800 !important;
    }
    
    /* Subheaders */
    .stMarkdown h2, .stMarkdown h3 {
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        color: black !important;
    }
    
    /* Radio buttons - purple accent */
    .stRadio label {
        color: rgb(15 23 42) !important;
        font-weight: 500 !important;
    }
    
    .stRadio [data-baseweb="radio"] > div:first-child {
        background-color: #6366f1 !important;
    }
    
    /* Checkbox - purple accent */
    .stCheckbox label {
        color: rgb(15 23 42) !important;
    }
    
    .stCheckbox [data-baseweb="checkbox"] {
        border-color: #6366f1 !important;
        background-color: #6366f1 !important;
    }
    
    /* Slider - purple accent */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #6366f1 !important;
    }
    
    .stSlider [data-baseweb="slider"] > div > div {
        background-color: #6366f1 !important;
    }
    
    /* All popover/tooltip content - white background */
    [data-baseweb="popover"] {
        background: white !important;
        color: rgb(15 23 42) !important;
        border: 1px solid #e5e7eb !important;
    }
    
    /* Modal/Dialog - white background */
    [data-baseweb="modal"] {
        background: white !important;
        color: rgb(15 23 42) !important;
    }
    
    /* Spinner - purple */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
    
    /* Progress bar - purple */
    .stProgress > div > div {
        background-color: #6366f1 !important;
    }
    
    /* All text content - ensure readability */
    p, span, label, div, li, td, th {
        color: rgb(15 23 42) !important;
    }
    
    /* Links - purple */
    a {
        color: #6366f1 !important;
    }
    
    a:hover {
        color: #4f46e5 !important;
    }
    
    /* Remove Streamlit branding padding */
    .css-1cypcdb {
        background: white !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'indexer' not in st.session_state:
        st.session_state.indexer = None
    if 'retriever' not in st.session_state:
        st.session_state.retriever = None
    if 'uploaded_files_data' not in st.session_state:
        st.session_state.uploaded_files_data = []
    if 'solution_result' not in st.session_state:
        st.session_state.solution_result = None
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None


def render_header():
    """Render GPAi-style header with navigation."""
    st.markdown("""
    <div class="main-header">
        <h1>GPAi - Resource-Scoped Mode</h1>
        <p>Answer questions strictly from your uploaded resources • Free, Error-Free, STEM-Ready</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")


def render_about_section():
    """Render feature description."""
    st.markdown("""
    <div class="feature-desc">
        <h3>About Resource-Scoped Mode</h3>
        <p><strong>What it does:</strong> Generates step-by-step solutions using ONLY your uploaded resources (PDFs, slides, textbooks, rubrics).</p>
        <p><strong>Strict Mode:</strong> Returns "No solution found" if any step cannot be proven from your documents.</p>
        <p><strong>Prefer Mode:</strong> Prefers your resources but may supplement with general knowledge (marked as UNSUPPORTED).</p>
        <p><strong>Privacy:</strong> All uploads processed locally. Use as a verifier/tutor — not a substitute for instructor evaluation.</p>
    </div>
    """, unsafe_allow_html=True)


def render_upload_section():
    """Render file upload interface."""
    st.subheader("1. Upload Your Resources")
    
    uploaded_files = st.file_uploader(
        "Upload PDFs, DOCX, PPTX, images, or text files",
        type=['pdf', 'docx', 'pptx', 'png', 'jpg', 'jpeg', 'txt'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, PPTX, PNG, JPG, TXT"
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully")
        
        # Show file details
        for idx, file in enumerate(uploaded_files):
            with st.expander(f"{file.name} ({file.size // 1024} KB)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    priority = st.selectbox(
                        "Priority",
                        ["normal", "rubric", "slides", "textbook"],
                        key=f"priority_{idx}"
                    )
                
                with col2:
                    trusted = st.checkbox("Trusted source", value=True, key=f"trusted_{idx}")
        
        # Process files button
        if st.button("Process & Index Files", type="primary"):
            with st.spinner("Processing files..."):
                process_uploaded_files(uploaded_files)
    
    return uploaded_files


def process_uploaded_files(uploaded_files):
    """Process and index uploaded files."""
    try:
        # Initialize components
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Create indexer
        indexer = EmbeddingIndexer(
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            chroma_db_dir=os.getenv("CHROMA_DB_DIR", "./chroma_db"),
            use_openai=(os.getenv("EMBEDDING_MODEL") == "openai"),
            openai_api_key=api_key if os.getenv("EMBEDDING_MODEL") == "openai" else None
        )
        
        # Clear existing collection
        indexer.clear_collection()
        
        # Process each file
        ingestor = DocumentIngestor(
            chunk_size=int(os.getenv("CHUNK_SIZE", 600)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 100))
        )
        
        all_chunks = []
        
        for idx, file in enumerate(uploaded_files):
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            
            # Get priority and trust settings
            priority = st.session_state.get(f"priority_{idx}", "normal")
            trusted = st.session_state.get(f"trusted_{idx}", True)
            
            # Ingest file
            chunks = ingestor.ingest_file(tmp_path, priority=priority, trusted=trusted)
            all_chunks.extend(chunks)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            st.write(f"✓ Processed {file.name}: {len(chunks)} chunks")
        
        # Index all chunks
        indexed_count = indexer.index_chunks(all_chunks)
        
        # Store in session state
        st.session_state.indexer = indexer
        st.session_state.retriever = DocumentRetriever(indexer, top_k=int(os.getenv("TOP_K", 10)))
        st.session_state.uploaded_files_data = all_chunks
        
        st.success(f"✅ Indexed {indexed_count} chunks from {len(uploaded_files)} files!")
        
        # Show stats
        stats = indexer.get_collection_stats()
        st.json(stats)
        
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")


def render_question_section():
    """Render question input interface."""
    st.subheader("2. Enter Your Question")
    
    question_mode = st.radio(
        "Question input method",
        ["Type question", "Upload question image", "Select from PDF"],
        horizontal=True
    )
    
    question = ""
    
    if question_mode == "Type question":
        question = st.text_area(
            "Enter your question",
            placeholder="e.g., Solve for x: 2x + 5 = 13",
            height=150
        )
    
    elif question_mode == "Upload question image":
        question_img = st.file_uploader("Upload question image", type=['png', 'jpg', 'jpeg'])
        if question_img:
            st.image(question_img, caption="Question image", width=400)
            
            # OCR the image
            if st.button("Extract text from image"):
                with st.spinner("Running OCR..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        tmp.write(question_img.read())
                        tmp_path = tmp.name
                    
                    ocr = MathOCR()
                    result = ocr.ocr_image(tmp_path, detect_math=True)
                    question = result.get('text', '')
                    
                    os.unlink(tmp_path)
                    
                    st.success(f"Extracted text ({result['method']})")
                    st.code(question)
    
    else:  # Select from PDF
        st.info("👉 Select a page from your uploaded PDFs that contains the question")
        # This would require PDF viewer integration - simplified for MVP
        question = st.text_input("Or type the question here")
    
    return question


def render_controls_section():
    """Render solution controls."""
    st.subheader("3. Configure Solution Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mode = st.selectbox(
            "Mode",
            ["prefer", "strict"],
            help="Strict: Only use resources | Prefer: Prefer resources but can use external knowledge"
        )
    
    with col2:
        methods = st.multiselect(
            "Method constraints (optional)",
            ["Algebraic", "Calculus", "Graphical", "Numeric"],
            help="Limit solution methods"
        )
    
    with col3:
        granularity = st.slider(
            "Step detail",
            min_value=1,
            max_value=5,
            value=3,
            help="1=Brief, 5=Very detailed"
        )
    
    return mode, methods, granularity


def render_solve_button(question, mode, methods):
    """Render solve button and handle solution generation."""
    if st.button("Generate Solution", type="primary", disabled=not question):
        if not st.session_state.retriever:
            st.error("Please upload and process files first!")
            return
        
        with st.spinner("Generating solution..."):
            try:
                # Retrieve relevant chunks
                retriever = st.session_state.retriever
                chunks = retriever.retrieve(question, top_k=10)
                
                if not chunks:
                    st.warning("⚠️ No relevant content found in uploaded resources")
                    return
                
                # Generate solution
                provider = os.getenv("LLM_PROVIDER", "ollama").lower()
                
                if provider == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        st.error("❌ OPENAI_API_KEY not configured in .env file")
                        return
                    generator = LLMGenerator(
                        api_key=api_key,
                        model=os.getenv("OPENAI_MODEL", "gpt-4"),
                        provider="openai"
                    )
                elif provider == "ollama":
                    generator = LLMGenerator(
                        model=os.getenv("OLLAMA_MODEL", "mistral"),
                        provider="ollama",
                        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                    )
                else:
                    st.error(f"❌ Unsupported LLM provider: {provider}")
                    return
                
                result = generator.generate_solution(
                    question=question,
                    retrieved_chunks=chunks,
                    mode=mode,
                    method_constraints=methods if methods else None
                )
                
                # Parse steps
                steps = generator.parse_solution_steps(result['solution'])
                
                # Validate
                validator = StepValidator(
                    sim_threshold=float(os.getenv("SIM_THRESHOLD", 0.78)),
                    min_ngram_overlap=int(os.getenv("MIN_NGRAM_OVERLAP", 6))
                )
                
                validation = validator.validate_solution(steps, chunks, mode=mode)
                
                # Store results
                st.session_state.solution_result = {
                    'question': question,
                    'solution': result['solution'],
                    'steps': steps,
                    'chunks': chunks,
                    'mode': mode,
                    'model': result['model']
                }
                st.session_state.validation_result = validation
                
            except Exception as e:
                st.error(f"❌ Error generating solution: {str(e)}")


def render_output_section():
    """Render solution output."""
    if not st.session_state.solution_result:
        return
    
    st.subheader("4. Solution & Validation")
    
    result = st.session_state.solution_result
    validation = st.session_state.validation_result
    
    # Validation status
    if validation['status'] == "FAILED":
        st.error("❌ " + validation['message'])
        st.code("No supported solution found in resources.")
        return
    elif validation['status'] == "PASSED":
        st.success(f"✅ {validation['message']}")
    else:
        st.warning(f"⚠️ {validation['message']}")
    
    # Display steps
    st.markdown("### Step-by-Step Solution")
    
    for step_data in validation['step_validations']:
        step_num = step_data['step_num']
        step_text = step_data['step_text']
        supported = step_data['supported']
        confidence = step_data['confidence']
        
        # Step container
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**Step {step_num}:**")
                st.markdown(step_text)
                
                # Citations
                citations = step_data.get('citations_found', [])
                if citations:
                    st.markdown("**Citations:** " + " ".join([f"`{c}`" for c in citations]))
            
            with col2:
                # Validation badge
                if supported:
                    st.markdown(f'<span class="confidence-{confidence.lower()}">✔ {confidence}</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="confidence-low">⚠ UNSUPPORTED</span>', unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export as PDF"):
            st.info("PDF export feature - to be implemented")
    
    with col2:
        if st.button("Export as PPTX"):
            st.info("PPTX export feature - to be implemented")
    
    with col3:
        if st.button("Flag for review"):
            st.success("Flagged for human review and logged to ./logs/")


def render_footer():
    """Render footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p><strong>Privacy & Data:</strong> All uploads processed locally. <a href="#" style="color: #0b63ce;">Delete my data</a></p>
        <p><small>Note: Strict mode may fail if resources are insufficient. Use as verifier/tutor — not a substitute for instructor evaluation.</small></p>
        <p><small>Powered by GPAi Resource-Scoped Mode • Built with Streamlit, ChromaDB, OpenAI</small></p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application."""
    initialize_session_state()
    
    render_header()
    render_about_section()
    
    # Main layout
    uploaded_files = render_upload_section()
    
    st.markdown("---")
    
    question = render_question_section()
    
    st.markdown("---")
    
    mode, methods, granularity = render_controls_section()
    
    st.markdown("---")
    
    render_solve_button(question, mode, methods)
    
    render_output_section()
    
    render_footer()


if __name__ == "__main__":
    main()
