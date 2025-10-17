"""
Validator module with textual similarity and symbolic verification.
"""

import re
import os
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sympy
from sympy.parsing.latex import parse_latex


class StepValidator:
    """Validates solution steps against retrieved chunks."""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        sim_threshold: float = 0.78,
        min_ngram_overlap: int = 6,
        log_dir: str = "./logs"
    ):
        """
        Initialize validator.
        
        Args:
            embedding_model: Model for computing embeddings
            sim_threshold: Minimum cosine similarity for text support
            min_ngram_overlap: Minimum token overlap required
            log_dir: Directory for validation logs
        """
        self.encoder = SentenceTransformer(embedding_model)
        self.sim_threshold = sim_threshold
        self.min_ngram_overlap = min_ngram_overlap
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        print(f"✓ Validator initialized (sim_threshold={sim_threshold}, ngram_overlap={min_ngram_overlap})")
    
    def validate_solution(
        self,
        solution_steps: List[Dict[str, Any]],
        retrieved_chunks: List[Dict[str, Any]],
        mode: str = "strict"
    ) -> Dict[str, Any]:
        """
        Validate all steps in a solution.
        
        Args:
            solution_steps: List of step dictionaries
            retrieved_chunks: List of retrieved chunk dictionaries
            mode: "strict" or "prefer"
            
        Returns:
            Validation result dictionary
        """
        validation_results = []
        all_supported = True
        
        # Extract chunk texts for validation
        chunk_texts = [chunk['chunk_text'] for chunk in retrieved_chunks]
        
        # Validate each step
        for step in solution_steps:
            step_text = step.get('text', '')
            
            # Skip empty steps
            if not step_text.strip():
                continue
            
            # Validate step
            step_validation = self._validate_step(step_text, chunk_texts, retrieved_chunks)
            
            validation_results.append({
                "step_num": step.get('step_num', 0),
                "step_text": step_text,
                "supported": step_validation['supported'],
                "support_type": step_validation['support_type'],
                "confidence": step_validation['confidence'],
                "best_match_similarity": step_validation.get('best_similarity', 0.0),
                "best_match_chunk": step_validation.get('best_chunk_id', None),
                "citations_found": step.get('citations', []),
                "unsupported_flag": step.get('unsupported', False)
            })
            
            if not step_validation['supported']:
                all_supported = False
        
        # Determine overall validation status
        if mode == "strict" and not all_supported:
            status = "FAILED"
            message = "No supported solution found in resources."
        elif mode == "strict" and all_supported:
            status = "PASSED"
            message = "All steps validated against resources."
        else:  # prefer mode
            supported_count = sum(1 for r in validation_results if r['supported'])
            total_count = len(validation_results)
            status = "PARTIAL" if supported_count < total_count else "PASSED"
            message = f"{supported_count}/{total_count} steps supported by resources."
        
        result = {
            "status": status,
            "message": message,
            "mode": mode,
            "all_supported": all_supported,
            "step_validations": validation_results,
            "total_steps": len(validation_results),
            "supported_steps": sum(1 for r in validation_results if r['supported'])
        }
        
        # Log validation
        self._log_validation(result)
        
        return result
    
    def _validate_step(
        self,
        step_text: str,
        chunk_texts: List[str],
        chunks_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate a single step.
        
        Args:
            step_text: The step text
            chunk_texts: List of chunk texts
            chunks_metadata: List of chunk metadata dicts
            
        Returns:
            Validation result for the step
        """
        # Check textual support
        text_support = self._check_textual_support(step_text, chunk_texts, chunks_metadata)
        
        # Check symbolic support if step contains math
        symbolic_support = self._check_symbolic_support(step_text, chunk_texts)
        
        # Determine overall support
        if text_support['supported']:
            return {
                "supported": True,
                "support_type": "textual",
                "confidence": text_support['confidence'],
                "best_similarity": text_support['similarity'],
                "best_chunk_id": text_support['chunk_id']
            }
        elif symbolic_support['supported']:
            return {
                "supported": True,
                "support_type": "symbolic",
                "confidence": symbolic_support['confidence'],
                "best_similarity": symbolic_support.get('similarity', 0.0),
                "best_chunk_id": symbolic_support.get('chunk_id', None)
            }
        else:
            return {
                "supported": False,
                "support_type": "none",
                "confidence": "LOW",
                "best_similarity": text_support['similarity'],
                "best_chunk_id": text_support.get('chunk_id', None)
            }
    
    def _check_textual_support(
        self,
        step_text: str,
        chunk_texts: List[str],
        chunks_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if step is textually supported by chunks."""
        if not chunk_texts:
            return {"supported": False, "similarity": 0.0, "confidence": "LOW"}
        
        # Compute embeddings
        step_embedding = self.encoder.encode([step_text])[0]
        chunk_embeddings = self.encoder.encode(chunk_texts)
        
        # Compute cosine similarities
        similarities = cosine_similarity([step_embedding], chunk_embeddings)[0]
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_similarity = float(similarities[best_idx])
        best_chunk = chunk_texts[best_idx]
        
        # Check token overlap
        overlap = self._compute_ngram_overlap(step_text, best_chunk)
        
        # Determine if supported
        supported = (best_similarity >= self.sim_threshold and 
                    overlap >= self.min_ngram_overlap)
        
        # Determine confidence
        if best_similarity >= 0.85:
            confidence = "HIGH"
        elif best_similarity >= self.sim_threshold:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        return {
            "supported": supported,
            "similarity": best_similarity,
            "token_overlap": overlap,
            "confidence": confidence,
            "chunk_id": chunks_metadata[best_idx].get('chunk_id', 'unknown') if chunks_metadata else None
        }
    
    def _check_symbolic_support(
        self,
        step_text: str,
        chunk_texts: List[str]
    ) -> Dict[str, Any]:
        """Check if step is symbolically/mathematically supported."""
        # Extract math expressions from step
        step_expressions = self._extract_math_expressions(step_text)
        
        if not step_expressions:
            return {"supported": False, "confidence": "LOW"}
        
        # Extract math from chunks
        for i, chunk_text in enumerate(chunk_texts):
            chunk_expressions = self._extract_math_expressions(chunk_text)
            
            # Try to verify symbolic equivalence
            for step_expr in step_expressions:
                for chunk_expr in chunk_expressions:
                    if self._are_symbolically_equivalent(step_expr, chunk_expr):
                        return {
                            "supported": True,
                            "confidence": "HIGH",
                            "chunk_id": f"chunk_{i}",
                            "step_expr": step_expr,
                            "chunk_expr": chunk_expr
                        }
        
        return {"supported": False, "confidence": "LOW"}
    
    def _extract_math_expressions(self, text: str) -> List[str]:
        """Extract mathematical expressions from text."""
        expressions = []
        
        # Extract LaTeX expressions
        latex_patterns = [
            r'\$([^\$]+)\$',  # Inline math
            r'\\\[(.+?)\\\]',  # Display math
            r'\\\((.+?)\\\)',  # Inline math alternative
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, text)
            expressions.extend(matches)
        
        # Extract equations (text with = sign and numbers/variables)
        equation_pattern = r'([a-zA-Z0-9\s\+\-\*/\^=\(\)\.]+=[a-zA-Z0-9\s\+\-\*/\^=\(\)\.]+)'
        equations = re.findall(equation_pattern, text)
        expressions.extend(equations)
        
        return [expr.strip() for expr in expressions if expr.strip()]
    
    def _are_symbolically_equivalent(self, expr1: str, expr2: str) -> bool:
        """
        Check if two expressions are symbolically equivalent.
        
        Args:
            expr1: First expression
            expr2: Second expression
            
        Returns:
            True if equivalent
        """
        try:
            # Try to parse as LaTeX first
            try:
                sym_expr1 = parse_latex(expr1)
                sym_expr2 = parse_latex(expr2)
            except:
                # Fallback to sympify
                sym_expr1 = sympy.sympify(expr1)
                sym_expr2 = sympy.sympify(expr2)
            
            # Check equivalence
            difference = sympy.simplify(sym_expr1 - sym_expr2)
            
            return difference == 0
        except Exception as e:
            # If parsing fails, do string comparison
            normalized1 = self._normalize_expression(expr1)
            normalized2 = self._normalize_expression(expr2)
            
            return normalized1 == normalized2
    
    def _normalize_expression(self, expr: str) -> str:
        """Normalize expression for comparison."""
        # Remove whitespace
        expr = re.sub(r'\s+', '', expr)
        # Convert to lowercase
        expr = expr.lower()
        # Standardize operators
        expr = expr.replace('*', '')  # Implicit multiplication
        expr = expr.replace('×', '')
        
        return expr
    
    def _compute_ngram_overlap(self, text1: str, text2: str, n: int = 3) -> int:
        """
        Compute n-gram overlap between two texts.
        
        Args:
            text1: First text
            text2: Second text
            n: N-gram size
            
        Returns:
            Number of overlapping n-grams
        """
        # Tokenize
        tokens1 = text1.lower().split()
        tokens2 = text2.lower().split()
        
        # Generate n-grams
        ngrams1 = set()
        for i in range(len(tokens1) - n + 1):
            ngram = ' '.join(tokens1[i:i+n])
            ngrams1.add(ngram)
        
        ngrams2 = set()
        for i in range(len(tokens2) - n + 1):
            ngram = ' '.join(tokens2[i:i+n])
            ngrams2.add(ngram)
        
        # Count overlaps
        overlap = len(ngrams1 & ngrams2)
        
        return overlap
    
    def _log_validation(self, validation_result: Dict[str, Any]):
        """Log validation results."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": validation_result['status'],
            "mode": validation_result['mode'],
            "total_steps": validation_result['total_steps'],
            "supported_steps": validation_result['supported_steps'],
            "step_details": validation_result['step_validations']
        }
        
        log_filename = f"validation_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        log_path = os.path.join(self.log_dir, log_filename)
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def validate_strict_mode(
    solution_text: str,
    chunks: List[Dict[str, Any]],
    generator
) -> Tuple[bool, str]:
    """
    Convenience function for strict mode validation.
    
    Args:
        solution_text: The generated solution
        chunks: Retrieved chunks
        generator: LLMGenerator instance for parsing
        
    Returns:
        Tuple of (is_valid, message or solution)
    """
    # Parse solution into steps
    steps = generator.parse_solution_steps(solution_text)
    
    # Validate
    validator = StepValidator()
    result = validator.validate_solution(steps, chunks, mode="strict")
    
    if result['status'] == "PASSED":
        return True, solution_text
    else:
        return False, "No supported solution found in resources."
