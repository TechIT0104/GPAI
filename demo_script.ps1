# Demo script for Resource-Scoped Mode (Windows PowerShell)
# Demonstrates happy path and strict mode failure

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Resource-Scoped Mode - Demo Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not detected" -ForegroundColor Yellow
    Write-Host "Run: venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host ""
}

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "Run: copy .env.example .env" -ForegroundColor Yellow
    exit 1
}

# Check if sample data exists
Write-Host "📂 Checking sample data..." -ForegroundColor Cyan
if (-not (Test-Path sample_data/instructor_solution.txt) -and -not (Test-Path sample_data/instructor_solution.pdf)) {
    Write-Host "Generating sample data..." -ForegroundColor Yellow
    python sample_data/generate_samples.py
}

Write-Host "✅ Sample data ready" -ForegroundColor Green
Write-Host ""

# Create demo directory
New-Item -ItemType Directory -Force -Path demo | Out-Null

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Demo 1: Happy Path (Strict Mode Success)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Setup:" -ForegroundColor Yellow
Write-Host "- Upload: sample_data/instructor_solution.txt (priority: rubric)"
Write-Host "- Question: Solve for x: 2x + 5 = 13"
Write-Host "- Mode: Strict"
Write-Host ""
Write-Host "Expected: Multi-step solution with citations, all steps validated ✅" -ForegroundColor Green
Write-Host ""

Write-Host "To run this demo manually:"
Write-Host "1. streamlit run app.py"
Write-Host "2. Upload sample_data/instructor_solution.txt with priority='rubric'"
Write-Host "3. Click 'Process & Index Files'"
Write-Host "4. Enter question: 'Solve for x: 2x + 5 = 13'"
Write-Host "5. Select Mode: 'strict'"
Write-Host "6. Click 'Generate Solution'"
Write-Host ""
Write-Host "Expected output: Step-by-step solution with inline citations"
Write-Host "Validation: All steps should show ✔ HIGH or ✔ MEDIUM confidence"
Write-Host ""

Read-Host "Press Enter to continue to Demo 2"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Demo 2: Strict Mode Failure" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Setup:" -ForegroundColor Yellow
Write-Host "- Upload: sample_data/textbook_excerpt.txt (about quadratics)"
Write-Host "- Question: Solve for x: 2x + 5 = 13 (linear equation)"
Write-Host "- Mode: Strict"
Write-Host ""
Write-Host "Expected: 'No supported solution found in resources.' ❌" -ForegroundColor Red
Write-Host ""

Write-Host "To run this demo manually:"
Write-Host "1. Clear previous uploads (reload app or use 'Delete my data')"
Write-Host "2. Upload sample_data/textbook_excerpt.txt"
Write-Host "3. Click 'Process & Index Files'"
Write-Host "4. Enter question: 'Solve for x: 2x + 5 = 13'"
Write-Host "5. Select Mode: 'strict'"
Write-Host "6. Click 'Generate Solution'"
Write-Host ""
Write-Host "Expected output: 'No supported solution found in resources.'"
Write-Host "Reason: Textbook excerpt is about quadratics, not linear equations"
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Running Tests" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "Run automated tests? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Running pytest..." -ForegroundColor Cyan
    pytest tests/ -v -s
    Write-Host ""
    Write-Host "✅ Tests completed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Demo Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start app: streamlit run app.py"
Write-Host "2. Try uploading your own PDFs/documents"
Write-Host "3. Experiment with strict vs prefer modes"
Write-Host "4. Check logs/ directory for audit trails"
Write-Host ""
Write-Host "For more info, see README.md"
