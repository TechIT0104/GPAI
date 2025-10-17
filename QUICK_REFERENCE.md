# Quick Reference Card

## 🚀 Quick Commands

```bash
# Setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env  # Add OPENAI_API_KEY

# Run
streamlit run app.py

# Test
pytest tests/ -v

# Demo
.\demo_script.ps1  # Windows
```

## 📝 Configuration (.env)

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SIM_THRESHOLD=0.78
MIN_NGRAM_OVERLAP=6
TOP_K=10
CHUNK_SIZE=600
CHUNK_OVERLAP=100
```

## 🎯 Key Features

| Feature | Location | Status |
|---------|----------|--------|
| Upload & Index | `backend/ingest.py` | ✅ |
| Retrieval | `backend/retrieve.py` | ✅ |
| LLM Generation | `backend/generator.py` | ✅ |
| Validation | `backend/validator.py` | ✅ |
| Streamlit UI | `app.py` | ✅ |
| Tests | `tests/` | ✅ 11/11 |

## 🔧 Common Tasks

### Change LLM Model
```bash
# In .env
OPENAI_MODEL=gpt-4-turbo  # or gpt-3.5-turbo
```

### Use OpenAI Embeddings
```bash
# In .env
EMBEDDING_MODEL=openai
```

### Adjust Validation Threshold
```bash
# In .env
SIM_THRESHOLD=0.70  # Lower = more lenient
MIN_NGRAM_OVERLAP=4  # Lower = more lenient
```

### Clear Database
```bash
rm -rf chroma_db/  # Linux/Mac
rmdir /s chroma_db  # Windows
```

## 📊 File Types Supported

- ✅ PDF (PyMuPDF)
- ✅ DOCX (python-docx)
- ✅ PPTX (python-pptx)
- ✅ Images (OCR with pytesseract/pix2tex)
- ✅ TXT (plain text)

## 🧪 Test Coverage

```bash
tests/test_ingest.py         # Document parsing
tests/test_retrieve.py       # Vector search
tests/test_strict_mode.py    # Validation (CRITICAL)
```

## 📁 Important Directories

| Directory | Purpose |
|-----------|---------|
| `backend/` | Core modules |
| `tests/` | Pytest tests |
| `sample_data/` | Demo files |
| `logs/` | Audit logs |
| `chroma_db/` | Vector index |

## ⚡ Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | `pip install -r requirements.txt` |
| OpenAI error | Check `.env` has `OPENAI_API_KEY` |
| ChromaDB error | Delete `chroma_db/` directory |
| Port in use | `streamlit run app.py --server.port 8502` |

## 🎓 Usage Modes

**Strict Mode:**
- Only uses uploaded resources
- Fails if any step unsupported
- Returns: "No supported solution found in resources."

**Prefer Mode:**
- Prefers uploaded resources
- Supplements with general knowledge
- Marks unsupported steps with (UNSUPPORTED)

## 📚 Documentation

- `README.md` - Full documentation
- `SETUP.md` - Quick setup guide
- `CHANGELOG.md` - Version history
- `PROJECT_SUMMARY.md` - Deliverable summary
- This file - Quick reference

## 🔗 External Links

- [OpenAI Platform](https://platform.openai.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

---

**Need help?** Check `README.md` § Troubleshooting or `SETUP.md`
