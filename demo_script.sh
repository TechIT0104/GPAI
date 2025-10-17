#!/bin/bash

# Demo script for Resource-Scoped Mode
# Demonstrates happy path and strict mode failure

echo "========================================="
echo "Resource-Scoped Mode - Demo Script"
echo "========================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo "Run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
    echo ""
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Copy .env.example to .env and add your OPENAI_API_KEY"
    echo "Run: cp .env.example .env"
    exit 1
fi

# Check if sample data exists
echo "📂 Checking sample data..."
if [ ! -f sample_data/instructor_solution.txt ] && [ ! -f sample_data/instructor_solution.pdf ]; then
    echo "Generating sample data..."
    python sample_data/generate_samples.py
fi

echo "✅ Sample data ready"
echo ""

# Create demo directory
mkdir -p demo

echo "========================================="
echo "Demo 1: Happy Path (Strict Mode Success)"
echo "========================================="
echo ""
echo "Setup:"
echo "- Upload: sample_data/instructor_solution.txt (priority: rubric)"
echo "- Question: Solve for x: 2x + 5 = 13"
echo "- Mode: Strict"
echo ""
echo "Expected: Multi-step solution with citations, all steps validated ✅"
echo ""

# Note: Actual demo would require Streamlit interaction
# This script documents the demo steps

echo "To run this demo manually:"
echo "1. streamlit run app.py"
echo "2. Upload sample_data/instructor_solution.txt with priority='rubric'"
echo "3. Click 'Process & Index Files'"
echo "4. Enter question: 'Solve for x: 2x + 5 = 13'"
echo "5. Select Mode: 'strict'"
echo "6. Click 'Generate Solution'"
echo ""
echo "Expected output: Step-by-step solution with inline citations"
echo "Validation: All steps should show ✔ HIGH or ✔ MEDIUM confidence"
echo ""

read -p "Press Enter to continue to Demo 2..."

echo ""
echo "========================================="
echo "Demo 2: Strict Mode Failure"
echo "========================================="
echo ""
echo "Setup:"
echo "- Upload: sample_data/textbook_excerpt.txt (about quadratics)"
echo "- Question: Solve for x: 2x + 5 = 13 (linear equation)"
echo "- Mode: Strict"
echo ""
echo "Expected: 'No supported solution found in resources.' ❌"
echo ""

echo "To run this demo manually:"
echo "1. Clear previous uploads (reload app or use 'Delete my data')"
echo "2. Upload sample_data/textbook_excerpt.txt"
echo "3. Click 'Process & Index Files'"
echo "4. Enter question: 'Solve for x: 2x + 5 = 13'"
echo "5. Select Mode: 'strict'"
echo "6. Click 'Generate Solution'"
echo ""
echo "Expected output: 'No supported solution found in resources.'"
echo "Reason: Textbook excerpt is about quadratics, not linear equations"
echo ""

echo "========================================="
echo "Demo 3: Prefer Mode (Partial Support)"
echo "========================================="
echo ""
echo "Setup: Same as Demo 2 but with Mode: 'prefer'"
echo ""
echo "Expected: Solution generated with some steps marked (UNSUPPORTED) ⚠️"
echo ""

echo "========================================="
echo "Running Tests"
echo "========================================="
echo ""

read -p "Run automated tests? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running pytest..."
    pytest tests/ -v -s
    echo ""
    echo "✅ Tests completed"
fi

echo ""
echo "========================================="
echo "Demo Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Start app: streamlit run app.py"
echo "2. Try uploading your own PDFs/documents"
echo "3. Experiment with strict vs prefer modes"
echo "4. Check logs/ directory for audit trails"
echo ""
echo "For more info, see README.md"
