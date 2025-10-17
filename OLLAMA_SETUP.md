# 🎯 Complete Ollama Setup Guide

## What You Need to Do Now

### 1️⃣ Install Ollama (5 minutes)

**Download and Install:**
- Open: https://ollama.com/download
- Download **Ollama for Windows**
- Run the installer (`OllamaSetup.exe`)
- Follow the installation wizard

**Verify Installation:**
Open a **NEW PowerShell window** and run:
```powershell
ollama --version
```
You should see: `ollama version 0.x.x`

---

### 2️⃣ Download Mistral Model (5-10 minutes)

```powershell
ollama pull mistral
```

**What's happening:**
- Downloads ~4GB Mistral 7B model
- Shows progress bar
- Stores locally for offline use

**Alternative models** (if you want different options):
```powershell
# Smaller, faster (2GB)
ollama pull llama3.2

# Coding-focused (4GB)
ollama pull codellama

# Math-focused (7GB)
ollama pull deepseek-math
```

---

### 3️⃣ Test Ollama (1 minute)

```powershell
ollama run mistral "Solve: 2x + 5 = 13"
```

You should see a step-by-step solution!

---

## Your `.env` File is Ready! ✅

The `.env` file is already configured for Ollama:

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

---

## 🚀 Next Steps (After Ollama is Installed)

### Run Tests:
```powershell
pytest tests/ -v
```

### Run Streamlit Demo:
```powershell
streamlit run app.py
```

---

## 🔄 Switching Between Providers Later

### To use OpenAI instead:
Edit `.env` and change:
```bash
# LLM_PROVIDER=ollama  # Comment out
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

### To use Google Gemini (free tier):
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-pro
```

---

## 💡 Why Ollama?

✅ **100% Free** - No API costs
✅ **Fast** - Runs locally on your GPU/CPU
✅ **Private** - Your data never leaves your machine
✅ **Offline** - Works without internet after model download
✅ **No Rate Limits** - Use as much as you want

---

## 🐛 Troubleshooting

### "ollama: command not found"
- Make sure you **close and reopen** PowerShell after installation
- Ollama adds itself to PATH during installation

### "Cannot connect to Ollama"
- Ollama runs as a background service automatically
- Check if it's running: `Get-Process ollama` in PowerShell
- Restart: `ollama serve` in a separate terminal

### Model too slow
- Try a smaller model: `ollama pull llama3.2`
- Or use GPU acceleration (if you have NVIDIA GPU)

### Want to see all available models?
```powershell
ollama list
```

---

## 📊 System Requirements

**Minimum:**
- 8GB RAM
- 10GB free disk space
- Windows 10/11

**Recommended:**
- 16GB RAM
- NVIDIA GPU with 6GB+ VRAM (for faster inference)
- 20GB free disk space (for multiple models)

---

## ✅ Checklist

Once you complete the steps, you should have:

- [ ] Ollama installed and running
- [ ] Mistral model downloaded
- [ ] Tested with `ollama run mistral "test"`
- [ ] `.env` file configured
- [ ] Sample data generated ✓ (already done!)

**You're almost ready to run the prototype!** 🎉

Let me know when Ollama is installed and we'll run the tests and demo!
