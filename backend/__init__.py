"""Backend package for Resource-Scoped Mode."""

from .ingest import DocumentIngestor, DocumentChunk, extract_file_metadata
from .ocr_math import MathOCR, extract_latex_from_image, extract_text_from_image
from .embed_and_index import EmbeddingIndexer
from .retrieve import DocumentRetriever, format_retrieved_chunks
from .generator import LLMGenerator, generate_step_by_step
from .validator import StepValidator, validate_strict_mode

__all__ = [
    'DocumentIngestor',
    'DocumentChunk',
    'extract_file_metadata',
    'MathOCR',
    'extract_latex_from_image',
    'extract_text_from_image',
    'EmbeddingIndexer',
    'DocumentRetriever',
    'format_retrieved_chunks',
    'LLMGenerator',
    'generate_step_by_step',
    'StepValidator',
    'validate_strict_mode'
]
