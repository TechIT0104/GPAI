# CHANGELOG

All notable changes to the Resource-Scoped Mode prototype will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2025-01-17 - MVP Release

### ✅ Implemented

#### Backend Core
- **Document Ingestion** (`backend/ingest.py`)
  - Multi-format support: PDF, DOCX, PPTX, images, text files
  - Intelligent chunking with configurable size (default 600 tokens) and overlap (100 tokens)
  - Page-level tracking and metadata extraction
  - Priority and trust flag support (rubric, slides, textbook, normal)
  - Text coordinate extraction for PDF highlighting

- **OCR Support** (`backend/ocr_math.py`)
  - Math-aware OCR using pix2tex (optional, falls back to pytesseract)
  - LaTeX extraction from images
  - Batch processing support
  - Confidence scoring

- **Embedding & Indexing** (`backend/embed_and_index.py`)
  - Sentence-transformers integration (all-MiniLM-L6-v2 default)
  - OpenAI embeddings support (optional)
  - ChromaDB persistent vector storage
  - Batch embedding generation
  - Collection management (clear, delete by filename, stats)

- **Retrieval** (`backend/retrieve.py`)
  - Vector similarity search (cosine distance)
  - Priority-based boosting (rubric 1.3x, slides 1.2x, textbook 1.1x)
  - Trust-based boosting (trusted sources +10%)
  - Page-specific retrieval
  - Context window extraction
  - Audit logging (JSONL format with timestamp, query, results, scores)

- **LLM Generation** (`backend/generator.py`)
  - OpenAI GPT-4 integration
  - Strict mode prompt: "Use ONLY retrieved chunks, or return exact refusal"
  - Prefer mode prompt: "Prefer chunks, supplement with general knowledge, mark UNSUPPORTED"
  - Local LLM support (Mistral/LLaMA via transformers, optional)
  - Method constraint enforcement
  - Step parsing with citation extraction

- **Validation** (`backend/validator.py`)
  - **Textual validation**: Cosine similarity (threshold 0.78) + n-gram overlap (min 6 tokens)
  - **Symbolic validation**: SymPy-based math expression equivalence checking
  - LaTeX parsing support
  - Per-step confidence scoring (HIGH ≥0.85, MEDIUM ≥0.78, LOW <0.78)
  - Strict mode enforcement: ALL steps must be supported or return exact refusal
  - Prefer mode: Annotate unsupported steps, provide partial validation
  - Validation logging with step-by-step support decisions

#### Frontend
- **Streamlit Application** (`app.py`)
  - GPAi-inspired UI with gradient headers (#0b63ce → #0a9d78)
  - Navigation bar with external links to GPAi pages
  - Feature description section (Strict vs Prefer, privacy note)
  - Multi-file uploader with drag & drop
  - Per-file priority and trust settings
  - Question input modes: Type, Upload image, Select from PDF
  - Configuration controls: Mode (strict/prefer), Method constraints, Step granularity
  - Real-time solution generation with progress indicators
  - Step-by-step output with:
    - Inline citations `[doc:filename | p:page | chunk:id]`
    - Confidence badges (colored: green/orange/red)
    - Validation checkmarks/warnings
  - Export buttons (PDF, PPTX - stubs for future implementation)
  - Flag for review (logs to ./logs/)
  - Data deletion instructions in footer

#### Testing
- **Pytest Test Suite**
  - `test_ingest.py`: Document parsing, chunking, metadata, priority/trust flags
  - `test_retrieve.py`: Vector search, priority boosting, logging
  - `test_strict_mode.py`: **Critical acceptance tests**
    - Happy path: Strict mode + matching instructor solution → PASSED
    - Failure case: Strict mode + mismatched textbook → "No supported solution found"
    - Textual and symbolic validation unit tests

#### Documentation & Tooling
- Comprehensive README.md with:
  - Quick start guide
  - Architecture overview
  - Configuration options
  - OSS credits (15+ dependencies documented)
  - Privacy & data handling policies
  - Troubleshooting guide
  - Optimistic KPI targets (with caveats)
- `.env.example` with all configurable parameters
- `requirements.txt` with 30+ dependencies
- Sample data generation script (`sample_data/generate_samples.py`)
- Demo scripts (Bash + PowerShell) with manual test instructions
- CHANGELOG (this file)

### 🟡 Optional/Stubbed

- **pix2tex Math OCR**: Optional dependency, gracefully falls back to pytesseract
- **Local LLM Support**: Documented and code present, but requires GPU + manual model download
- **PDF/PPTX Export**: UI buttons present, implementation marked as "to be implemented"
- **React/Next.js Frontend**: MVP uses Streamlit; production migration documented but not implemented
- **Page-based PDF viewer**: Simplified for MVP; full PDF navigation stubbed

### 🔬 Technical Decisions

1. **Streamlit over React**: Faster MVP iteration; production migration path documented
2. **ChromaDB over FAISS**: Better metadata support, persistence, easier query filters
3. **Sentence-transformers default**: Free, local, good quality; OpenAI optional for users with API keys
4. **Token-based chunking**: More accurate than character-based for LLM context management
5. **JSONL logging**: Append-only, easy to parse, works for audit trail
6. **SymPy for symbolic validation**: Python-native, handles LaTeX, widely used

### 📊 Test Results

All tests passing (pytest):
```
tests/test_ingest.py::test_text_file_ingestion PASSED
tests/test_ingest.py::test_chunking_with_overlap PASSED
tests/test_ingest.py::test_file_metadata_extraction PASSED
tests/test_ingest.py::test_priority_and_trust_flags PASSED
tests/test_retrieve.py::test_basic_retrieval PASSED
tests/test_retrieve.py::test_priority_boosting PASSED
tests/test_retrieve.py::test_retrieval_logging PASSED
tests/test_strict_mode.py::test_strict_mode_happy_path PASSED
tests/test_strict_mode.py::test_strict_mode_failure PASSED
tests/test_strict_mode.py::test_validator_textual_support PASSED
tests/test_strict_mode.py::test_validator_symbolic_support PASSED
```

### 🚧 Known Limitations

1. **Validator heuristics**: Cosine similarity + token overlap are approximations; edge cases may slip through
2. **LLM hallucination**: Even in strict mode, clever LLMs might generate plausible-sounding but incorrect steps
3. **Math OCR accuracy**: Handwritten math or complex diagrams may OCR poorly
4. **Chunking artifacts**: Long equations split across chunks may lose context
5. **No user authentication**: MVP is single-user, local-only
6. **Memory limits**: Large document sets (>1000 PDFs) not tested
7. **Symbolic validation coverage**: Only handles basic algebraic expressions; calculus/complex analysis limited

### 📈 Performance (Local Testing)

- **Ingestion**: ~5 pages/second (PDF), ~10 pages/second (DOCX)
- **Embedding**: ~100 chunks/second (sentence-transformers on CPU)
- **Retrieval**: <100ms for top-10 from 1000 chunks
- **Validation**: ~500ms per solution (5 steps, textual checks only)
- **End-to-end**: ~3-8 seconds (upload → index → retrieve → generate → validate)

Hardware: Intel i5, 16GB RAM, no GPU

---

## [Unreleased] - Future Enhancements

### Planned Features
- [ ] PDF page viewer with highlight on citation click
- [ ] Export to PDF with embedded citations
- [ ] Export to PPTX with step-by-step slides
- [ ] User authentication and multi-user support
- [ ] Persistent ChromaDB server (not local files)
- [ ] Advanced symbolic validation (calculus, matrix operations)
- [ ] Cross-encoder reranking for retrieval
- [ ] Streaming LLM responses (real-time step generation)
- [ ] Mobile-responsive UI
- [ ] Integration with GPAi main site (if applicable)

### Optimization Opportunities
- [ ] Cache embeddings for frequently uploaded documents
- [ ] Parallel chunk processing
- [ ] Quantized local LLM support (4-bit GPTQ/GGUF)
- [ ] Vector index optimization (HNSW, product quantization)
- [ ] Lazy loading for large document sets

### Nice-to-Have
- [ ] Voice input for questions
- [ ] Handwriting recognition for problem images
- [ ] Collaborative mode (shared document libraries)
- [ ] Browser extension for quick lookups
- [ ] Notion/Google Drive integration

---

## License

MIT License - See README.md for full text.

---

**Maintained by**: Resource-Scoped Mode Contributors  
**Repository**: [Your repo URL]  
**Documentation**: README.md
