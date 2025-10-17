"""
Generate sample PDF files for testing.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os


def create_instructor_solution_pdf(output_path):
    """Create a sample instructor solution PDF."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, height - inch, "Instructor Solution: Solving Linear Equations")
    
    # Problem
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, height - 1.5*inch, "Problem:")
    c.setFont("Helvetica", 11)
    c.drawString(inch, height - 1.8*inch, "Solve for x: 2x + 5 = 13")
    
    # Solution steps
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, height - 2.3*inch, "Step-by-Step Solution:")
    
    c.setFont("Helvetica", 11)
    y = height - 2.6*inch
    
    steps = [
        "Step 1: Subtract 5 from both sides",
        "        2x + 5 - 5 = 13 - 5",
        "        2x = 8",
        "",
        "Step 2: Divide both sides by 2",
        "        2x / 2 = 8 / 2",
        "        x = 4",
        "",
        "Step 3: Verify the solution",
        "        Substitute x = 4 back into the original equation:",
        "        2(4) + 5 = 13",
        "        8 + 5 = 13",
        "        13 = 13 ✓",
        "",
        "Therefore, x = 4 is the solution."
    ]
    
    for step in steps:
        c.drawString(inch, y, step)
        y -= 0.25*inch
    
    # Method note
    c.setFont("Helvetica-Bold", 10)
    y -= 0.5*inch
    c.drawString(inch, y, "Method: Algebraic manipulation using inverse operations")
    
    c.save()
    print(f"Created: {output_path}")


def create_textbook_excerpt_pdf(output_path):
    """Create a sample textbook excerpt PDF."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, height - inch, "Chapter 3: Quadratic Equations")
    
    # Content
    c.setFont("Helvetica", 11)
    y = height - 1.5*inch
    
    content = [
        "3.1 Introduction to Quadratic Equations",
        "",
        "A quadratic equation is a second-degree polynomial equation in a single variable x,",
        "with the general form:",
        "",
        "        ax² + bx + c = 0",
        "",
        "where a ≠ 0. The solutions can be found using the quadratic formula:",
        "",
        "        x = (-b ± √(b² - 4ac)) / 2a",
        "",
        "3.2 Solving Methods",
        "",
        "There are several methods to solve quadratic equations:",
        "",
        "1. Factoring: When the equation can be factored into (x - r₁)(x - r₂) = 0",
        "",
        "2. Quadratic Formula: Always works, especially when factoring is difficult",
        "",
        "3. Completing the Square: Useful for deriving the quadratic formula",
        "",
        "4. Graphical Method: Finding x-intercepts of the parabola y = ax² + bx + c",
        "",
        "Example: Solve x² - 5x + 6 = 0",
        "This factors to (x - 2)(x - 3) = 0",
        "Therefore, x = 2 or x = 3"
    ]
    
    for line in content:
        c.drawString(inch, y, line)
        y -= 0.25*inch
    
    c.save()
    print(f"Created: {output_path}")


def create_problem_image_description(output_path):
    """Create a simple problem as text (since we need actual image generation)."""
    # For MVP, we'll create a text file that describes what the image would contain
    with open(output_path.replace('.png', '.txt'), 'w') as f:
        f.write("Problem Image Content:\n\n")
        f.write("Question: Solve the system of equations:\n")
        f.write("2x + 3y = 12\n")
        f.write("x - y = 1\n")
    
    print(f"Created description: {output_path.replace('.png', '.txt')}")


def main():
    """Generate all sample files."""
    sample_dir = "./sample_data"
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create PDFs
    create_instructor_solution_pdf(os.path.join(sample_dir, "instructor_solution.pdf"))
    create_textbook_excerpt_pdf(os.path.join(sample_dir, "textbook_excerpt.pdf"))
    create_problem_image_description(os.path.join(sample_dir, "problem_image.png"))
    
    print("\n✅ Sample data files created successfully!")


if __name__ == "__main__":
    # Check if reportlab is available
    try:
        main()
    except ImportError:
        print("reportlab not installed. Install with: pip install reportlab")
        print("Creating simple text versions instead...")
        
        sample_dir = "./sample_data"
        os.makedirs(sample_dir, exist_ok=True)
        
        # Create text versions
        with open(os.path.join(sample_dir, "instructor_solution.txt"), 'w') as f:
            f.write("Instructor Solution: Solving Linear Equations\n\n")
            f.write("Problem: Solve for x: 2x + 5 = 13\n\n")
            f.write("Step 1: Subtract 5 from both sides\n")
            f.write("2x + 5 - 5 = 13 - 5\n")
            f.write("2x = 8\n\n")
            f.write("Step 2: Divide both sides by 2\n")
            f.write("2x / 2 = 8 / 2\n")
            f.write("x = 4\n\n")
            f.write("Step 3: Verify\n")
            f.write("2(4) + 5 = 13 ✓\n")
        
        with open(os.path.join(sample_dir, "textbook_excerpt.txt"), 'w') as f:
            f.write("Chapter 3: Quadratic Equations\n\n")
            f.write("A quadratic equation has the form: ax² + bx + c = 0\n")
            f.write("Solutions: x = (-b ± √(b² - 4ac)) / 2a\n")
        
        print("✅ Text versions created!")
