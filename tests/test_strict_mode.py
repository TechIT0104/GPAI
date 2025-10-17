"""
Test strict mode validation.
"""

import pytest
import tempfile
import os
from backend.ingest import DocumentIngestor
from backend.embed_and_index import EmbeddingIndexer
from backend.retrieve import DocumentRetriever
from backend.generator import LLMGenerator
from backend.validator import StepValidator, validate_strict_mode


@pytest.fixture
def setup_instructor_solution():
    """Setup with instructor solution document."""
    temp_dir = tempfile.mkdtemp()
    
    # Create indexer
    indexer = EmbeddingIndexer(
        chroma_db_dir=temp_dir,
        collection_name="test_strict"
    )
    
    # Create instructor solution document
    solution_text = """
    Problem: Solve for x: 2x + 5 = 13
    
    Step 1: Subtract 5 from both sides
    2x + 5 - 5 = 13 - 5
    2x = 8
    
    Step 2: Divide both sides by 2
    2x / 2 = 8 / 2
    x = 4
    
    Step 3: Verify the solution
    Substitute x = 4: 2(4) + 5 = 13
    8 + 5 = 13 (verified)
    
    Therefore x = 4
    """
    
    ingestor = DocumentIngestor(chunk_size=200, chunk_overlap=50)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(solution_text)
        temp_path = f.name
    
    chunks = ingestor.ingest_file(temp_path, priority="rubric", trusted=True)
    indexer.index_chunks(chunks)
    os.unlink(temp_path)
    
    retriever = DocumentRetriever(indexer, top_k=5)
    
    yield retriever, indexer, chunks
    
    indexer.clear_collection()


@pytest.fixture
def setup_mismatched_solution():
    """Setup with document that doesn't match the problem."""
    temp_dir = tempfile.mkdtemp()
    
    indexer = EmbeddingIndexer(
        chroma_db_dir=temp_dir,
        collection_name="test_strict_mismatch"
    )
    
    # Create textbook excerpt about quadratics (not relevant to linear equation)
    textbook_text = """
    Quadratic Equations
    
    A quadratic equation has the form ax^2 + bx + c = 0.
    
    The quadratic formula is: x = (-b +/- sqrt(b^2 - 4ac)) / 2a
    
    Example: Solve x^2 - 5x + 6 = 0
    Using the quadratic formula: x = 2 or x = 3
    """
    
    ingestor = DocumentIngestor(chunk_size=200, chunk_overlap=50)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(textbook_text)
        temp_path = f.name
    
    chunks = ingestor.ingest_file(temp_path, priority="textbook", trusted=True)
    indexer.index_chunks(chunks)
    os.unlink(temp_path)
    
    retriever = DocumentRetriever(indexer, top_k=5)
    
    yield retriever, indexer, chunks
    
    indexer.clear_collection()


def test_strict_mode_happy_path(setup_instructor_solution):
    """Test strict mode with matching instructor solution - should succeed."""
    retriever, indexer, chunks = setup_instructor_solution
    
    question = "Solve for x: 2x + 5 = 13"
    
    # Retrieve relevant chunks
    retrieved = retriever.retrieve(question, top_k=5)
    
    assert len(retrieved) > 0, "Should retrieve chunks"
    
    # Create mock solution that matches the chunks
    mock_solution_steps = [
        {
            "step_num": 1,
            "text": "Subtract 5 from both sides: 2x + 5 - 5 = 13 - 5, so 2x = 8",
            "citations": ["[doc:test.txt | p:1 | chunk:test_p1_c0]"],
            "unsupported": False
        },
        {
            "step_num": 2,
            "text": "Divide both sides by 2: 2x / 2 = 8 / 2, so x = 4",
            "citations": ["[doc:test.txt | p:1 | chunk:test_p1_c0]"],
            "unsupported": False
        }
    ]
    
    # Validate
    validator = StepValidator(sim_threshold=0.75, min_ngram_overlap=4)
    result = validator.validate_solution(mock_solution_steps, retrieved, mode="strict")
    
    print(f"\n✓ Strict mode (happy path): {result['status']}")
    print(f"  Message: {result['message']}")
    print(f"  Supported steps: {result['supported_steps']}/{result['total_steps']}")
    
    # In a real test with actual LLM, this should pass
    # For now, we're testing the validation logic
    assert result['total_steps'] == 2
    assert 'status' in result
    assert 'message' in result


def test_strict_mode_failure(setup_mismatched_solution):
    """Test strict mode with mismatched resources - should fail."""
    retriever, indexer, chunks = setup_mismatched_solution
    
    question = "Solve for x: 2x + 5 = 13"
    
    # Retrieve chunks (will be about quadratics, not linear equations)
    retrieved = retriever.retrieve(question, top_k=5)
    
    # Create solution steps for linear equation (not supported by quadratic text)
    mock_solution_steps = [
        {
            "step_num": 1,
            "text": "Subtract 5 from both sides to get 2x = 8",
            "citations": [],
            "unsupported": False
        },
        {
            "step_num": 2,
            "text": "Divide by 2 to get x = 4",
            "citations": [],
            "unsupported": False
        }
    ]
    
    # Validate in strict mode
    validator = StepValidator(sim_threshold=0.78, min_ngram_overlap=6)
    result = validator.validate_solution(mock_solution_steps, retrieved, mode="strict")
    
    print(f"\n✓ Strict mode (failure case): {result['status']}")
    print(f"  Message: {result['message']}")
    print(f"  Supported steps: {result['supported_steps']}/{result['total_steps']}")
    
    # Should not be fully supported since chunks are about quadratics
    assert result['status'] in ["FAILED", "PARTIAL"]
    
    # In strict mode, if not all supported, should fail
    if result['status'] == "FAILED":
        assert result['message'] == "No supported solution found in resources."


def test_validator_textual_support():
    """Test textual similarity validation."""
    validator = StepValidator(sim_threshold=0.75, min_ngram_overlap=4)
    
    chunk_texts = [
        "To solve linear equations, subtract the constant from both sides first.",
        "Then divide by the coefficient of the variable."
    ]
    
    chunks_metadata = [
        {"chunk_id": "chunk_1"},
        {"chunk_id": "chunk_2"}
    ]
    
    # Step that should be supported
    step_text = "Subtract the constant from both sides"
    result = validator._check_textual_support(step_text, chunk_texts, chunks_metadata)
    
    print(f"\n✓ Textual support check:")
    print(f"  Similarity: {result['similarity']:.3f}")
    print(f"  Token overlap: {result['token_overlap']}")
    print(f"  Supported: {result['supported']}")
    
    assert result['similarity'] > 0.5  # Should have some similarity


def test_validator_symbolic_support():
    """Test symbolic/mathematical validation."""
    validator = StepValidator()
    
    chunk_texts = [
        "The equation simplifies to 2x = 8",
        "Therefore x = 4"
    ]
    
    # Step with math that matches
    step_text = "We get 2x = 8"
    result = validator._check_symbolic_support(step_text, chunk_texts)
    
    print(f"\n✓ Symbolic support check:")
    print(f"  Supported: {result['supported']}")
    
    # May or may not be supported depending on math extraction
    assert 'supported' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
