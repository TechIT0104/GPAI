# GPAi Resource-Scoped Mode

Welcome! This is a working prototype that helps students and educators solve STEM problems using only the materials they've uploaded. Think of it as a smart tutor that only references your textbooks, lecture notes, and assignments.

## What Does It Do?

Upload your study materials (PDFs, slides, textbooks, assignments), ask a question, and get step-by-step solutions that are **grounded in your documents**. Every solution includes citations showing exactly where the information came from.

### Two Modes:

- **Strict Mode**: Only uses your uploaded materials. If the answer isn't in your docs, it will tell you honestly rather than making something up.
- **Prefer Mode**: Prefers your materials but can supplement with general knowledge when needed (clearly marked).

Every step shows where it came from: `[doc:filename | p:page | chunk:id]`

## Getting Started

### What You'll Need

- Python 3.8 or newer
- An LLM provider (we support Ollama for free local processing, or OpenAI/Gemini with API keys)
- That's it! Everything else installs automatically.

### Installation

```bash
# Navigate to the project folder
cd resource_scoped_proto

# Create a virtual environment (keeps things tidy)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install everything
pip install -r requirements.txt

# Set up your configuration
copy .env.example .env
```

Now edit `.env` and choose your LLM provider:

**Option 1: Free Local Processing (Ollama)**
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
```

**Option 2: OpenAI (requires API key)**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

### Try It Out

```bash
# Run the app
streamlit run app.py
```

Your browser will open to `http://localhost:8501`

## How to Use

### 1. Upload Your Materials

Drag and drop PDFs, Word docs, PowerPoint slides, images, or text files. Set priorities so the system knows what to trust most:
- Instructor solutions → "rubric"
- Lecture slides → "slides"
- Textbook chapters → "textbook"

The app will break your documents into chunks and index them for quick retrieval.

### 2. Ask Your Question

Three ways to ask:
- Type directly in the text box
- Upload an image of the problem
- Select a specific page from your PDFs

### 3. Choose Your Mode

- **Strict**: Only uses your uploads. Won't guess or make things up.
- **Prefer**: Tries to use your materials first, but can supplement with general knowledge if needed.

### 4. Get Your Solution

Hit "Generate Solution" and watch as the system:
- Finds relevant sections from your documents
- Builds a step-by-step solution
- Shows you exactly where each step comes from

### 5. Review and Export

Click any citation to see the source text. Export your solution as PDF or PowerPoint, or flag it for instructor review.

## Project Structure

```
resource_scoped_proto/
├── app.py                      # Main web interface
├── backend/
│   ├── ingest.py               # Reads and chunks documents
│   ├── ocr_math.py             # Extracts text from images
│   ├── embed_and_index.py      # Creates searchable vector database
│   ├── retrieve.py             # Finds relevant document chunks
│   ├── generator.py            # Generates solutions using LLM
│   └── validator.py            # Verifies steps against sources
├── sample_data/                # Example files for testing
├── tests/                      # Test suite
├── logs/                       # Audit trails
├── requirements.txt            # Dependencies
└── .env                        # Your configuration
```

### How It Works

1. Your documents get split into searchable chunks
2. When you ask a question, the system finds relevant chunks
3. An LLM generates a solution using those chunks
4. Every step is verified against your source material
5. You see the final solution with citations

## Configuration

You can tweak settings in your `.env` file. Here are the important ones:

```bash
# Which LLM provider to use
LLM_PROVIDER=ollama             # or openai, gemini

# For Ollama (free, local)
OLLAMA_MODEL=mistral

# For OpenAI (paid)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# For Gemini (paid)
GEMINI_API_KEY=your_key_here

# How strict should validation be?
SIM_THRESHOLD=0.78              # Higher = more strict (0.70-0.85 recommended)

# How many document chunks to retrieve?
TOP_K=10                        # More = better context but slower
```

## Testing

Make sure everything works:

```bash
pytest tests/ -v
```

The tests check:
- Document parsing and chunking
- Vector search accuracy
- Strict mode behavior (rejects unsupported solutions)
- Priority boosting (prefers instructor solutions over textbooks)

## Built With

- **[Streamlit](https://streamlit.io/)** - Web interface
- **[ChromaDB](https://www.trychroma.com/)** - Vector database
- **[sentence-transformers](https://www.sbert.net/)** - Document embeddings
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - PDF processing
- **[SymPy](https://www.sympy.org/)** - Math validation
- Inspired by [PaperQA](https://github.com/whitead/paper-qa) and other RAG projects

## Privacy

Your data stays on your machine. Documents are stored locally in `./uploads/` and `./chroma_db/`. 

The only external connection is to your chosen LLM provider:
- **Ollama**: Runs entirely locally (no data leaves your machine)
- **OpenAI/Gemini**: Sends queries to their API

To delete everything:
```bash
rm -rf chroma_db/ uploads/ logs/
```

## Important Notes

**This is a learning tool, not a substitute for your instructor.**

- Strict mode might reject valid solutions if your uploads don't have enough detail
- The validator uses similarity matching and isn't perfect
- Always double-check solutions, especially for exams or assignments
- Works best with clear, well-formatted source materials

## Troubleshooting

**ChromaDB won't start?**
Delete the `chroma_db/` folder and try again.

**Strict mode rejects everything?**
Lower `SIM_THRESHOLD` in your `.env` to 0.70 (more lenient) or check that your uploads actually contain the solution method.

**Need OCR for images?**
Install Tesseract: [tesseract-ocr.github.io](https://tesseract-ocr.github.io)

## License

MIT License - Free to use, modify, and distribute.

---

**Built for students and educators. Use it as a study aid, not a replacement for learning.**
