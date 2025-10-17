# Quick Setup Guide

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] Git (optional, for cloning)
- [ ] OpenAI API key (required for LLM)
- [ ] Tesseract OCR (optional, for image text extraction)

## Step-by-Step Installation

### 1. Extract/Clone Repository

```bash
cd resource_scoped_proto
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This will take 5-10 minutes. The installation includes:
- Streamlit (web framework)
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- OpenAI SDK
- Document parsers (PyMuPDF, python-docx, python-pptx)
- Validation tools (SymPy, scikit-learn)

### 4. Configure Environment

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

**Get an API key:** https://platform.openai.com/api-keys

### 5. Generate Sample Data

```bash
python sample_data/generate_samples.py
```

This creates test files for demos.

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## First-Time Use

1. **Upload a document**: Try `sample_data/instructor_solution.txt`
2. **Set priority**: Choose "rubric"
3. **Click**: "Process & Index Files"
4. **Enter question**: "Solve for x: 2x + 5 = 13"
5. **Select mode**: "strict"
6. **Click**: "Generate Solution"

You should see a step-by-step solution with citations!

## Troubleshooting

### "Module not found" errors

```bash
# Make sure venv is activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### "OpenAI API key not found"

- Check that `.env` file exists in the project root
- Verify `OPENAI_API_KEY=sk-...` is set (no quotes, no spaces)
- Restart the Streamlit app after editing `.env`

### "ChromaDB error"

```bash
# Delete the database and restart
rm -rf chroma_db/
# or on Windows:
rmdir /s chroma_db
```

### "Port already in use"

```bash
# Use a different port
streamlit run app.py --server.port 8502
```

## Optional: Install Tesseract OCR

For image text extraction:

**Windows:**
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

**Mac:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

## Optional: Install pix2tex (Math OCR)

```bash
pip install pix2tex
```

Note: This downloads a ~2GB model on first use.

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_strict_mode.py -v -s

# With coverage
pytest tests/ --cov=backend
```

## Next Steps

- Read the full [README.md](README.md) for architecture details
- Try uploading your own PDFs
- Experiment with strict vs prefer modes
- Check `logs/` directory for retrieval audit trails

## Getting Help

- Check [README.md](README.md) Troubleshooting section
- Review error logs in terminal
- Open an issue in the repository

---

**Ready to go?** Run `streamlit run app.py` and start solving! 🚀
