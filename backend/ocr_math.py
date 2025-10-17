"""
OCR module with math-aware OCR using pix2tex and pytesseract fallback.
"""

import os
from typing import Optional, Dict, Any
from PIL import Image
import pytesseract

# Try to import pix2tex (optional)
PIX2TEX_AVAILABLE = False
try:
    from pix2tex.cli import LatexOCR
    PIX2TEX_AVAILABLE = True
except ImportError:
    print("Warning: pix2tex not installed. Using pytesseract fallback for all OCR.")
    print("Install with: pip install pix2tex")


class MathOCR:
    """Math-aware OCR with pix2tex and pytesseract fallback."""
    
    def __init__(self, use_pix2tex: bool = True):
        """
        Initialize OCR engines.
        
        Args:
            use_pix2tex: Whether to use pix2tex for math OCR
        """
        self.use_pix2tex = use_pix2tex and PIX2TEX_AVAILABLE
        
        if self.use_pix2tex:
            try:
                self.latex_ocr = LatexOCR()
                print("✓ pix2tex LaTeX OCR initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize pix2tex: {e}")
                self.use_pix2tex = False
        
        # Test pytesseract availability
        try:
            pytesseract.get_tesseract_version()
            print("✓ pytesseract initialized")
        except Exception as e:
            print(f"Warning: pytesseract not available: {e}")
            print("Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    
    def ocr_image(self, image_path: str, detect_math: bool = True) -> Dict[str, Any]:
        """
        Perform OCR on an image.
        
        Args:
            image_path: Path to image file
            detect_math: Whether to use math-aware OCR
            
        Returns:
            Dictionary with OCR results
        """
        image = Image.open(image_path)
        
        result = {
            "text": "",
            "latex": "",
            "method": "",
            "confidence": 0.0
        }
        
        # Try pix2tex for math if available and requested
        if detect_math and self.use_pix2tex:
            try:
                latex = self.latex_ocr(image)
                result["latex"] = latex
                result["text"] = latex  # Use LaTeX as primary text
                result["method"] = "pix2tex"
                result["confidence"] = 0.9  # pix2tex doesn't provide confidence
                return result
            except Exception as e:
                print(f"pix2tex failed: {e}, falling back to pytesseract")
        
        # Fallback to pytesseract
        try:
            text = pytesseract.image_to_string(image)
            result["text"] = text.strip()
            result["method"] = "pytesseract"
            
            # Try to get confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            if confidences:
                result["confidence"] = sum(confidences) / len(confidences) / 100.0
            else:
                result["confidence"] = 0.0
            
        except Exception as e:
            print(f"pytesseract failed: {e}")
            result["text"] = "[OCR failed]"
            result["method"] = "failed"
            result["confidence"] = 0.0
        
        return result
    
    def ocr_pdf_page(self, pdf_path: str, page_num: int, detect_math: bool = True) -> Dict[str, Any]:
        """
        Perform OCR on a specific PDF page.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-indexed)
            detect_math: Whether to use math-aware OCR
            
        Returns:
            Dictionary with OCR results
        """
        from pdf2image import convert_from_path
        
        # Convert page to image
        images = convert_from_path(
            pdf_path,
            first_page=page_num,
            last_page=page_num,
            dpi=200
        )
        
        if not images:
            return {
                "text": "",
                "latex": "",
                "method": "failed",
                "confidence": 0.0
            }
        
        # Save temp image and run OCR
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            images[0].save(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = self.ocr_image(tmp_path, detect_math=detect_math)
        finally:
            os.unlink(tmp_path)
        
        return result
    
    def detect_math_content(self, text: str) -> bool:
        """
        Heuristic to detect if text likely contains mathematical content.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if math content detected
        """
        math_indicators = [
            '=', '+', '-', '×', '÷', '∫', '∑', '√', '^',
            'sin', 'cos', 'tan', 'log', 'ln',
            '\\frac', '\\int', '\\sum', '\\sqrt',
            r'\(', r'\)', r'\[', r'\]'
        ]
        
        return any(indicator in text.lower() for indicator in math_indicators)
    
    def batch_ocr(self, image_paths: list, detect_math: bool = True) -> list:
        """
        Perform OCR on multiple images.
        
        Args:
            image_paths: List of image file paths
            detect_math: Whether to use math-aware OCR
            
        Returns:
            List of OCR result dictionaries
        """
        results = []
        
        for image_path in image_paths:
            try:
                result = self.ocr_image(image_path, detect_math=detect_math)
                result["source_file"] = os.path.basename(image_path)
                results.append(result)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                results.append({
                    "text": "",
                    "latex": "",
                    "method": "failed",
                    "confidence": 0.0,
                    "source_file": os.path.basename(image_path),
                    "error": str(e)
                })
        
        return results


def extract_latex_from_image(image_path: str) -> str:
    """
    Convenience function to extract LaTeX from an image.
    
    Args:
        image_path: Path to image file
        
    Returns:
        LaTeX string
    """
    ocr = MathOCR(use_pix2tex=True)
    result = ocr.ocr_image(image_path, detect_math=True)
    return result.get("latex", result.get("text", ""))


def extract_text_from_image(image_path: str) -> str:
    """
    Convenience function to extract plain text from an image.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Plain text string
    """
    ocr = MathOCR(use_pix2tex=False)
    result = ocr.ocr_image(image_path, detect_math=False)
    return result.get("text", "")
