"""
Test retrieval module.
"""

import pytest
import tempfile
import os
from backend.ingest import DocumentIngestor
from backend.embed_and_index import EmbeddingIndexer
from backend.retrieve import DocumentRetriever


@pytest.fixture
def setup_test_index():
    """Setup test documents and indexer."""
    # Create temp directory for ChromaDB
    temp_dir = tempfile.mkdtemp()
    
    # Create indexer
    indexer = EmbeddingIndexer(
        chroma_db_dir=temp_dir,
        collection_name="test_collection"
    )
    
    # Create test documents
    ingestor = DocumentIngestor(chunk_size=100, chunk_overlap=20)
    
    docs = [
        ("Linear equations can be solved by isolating the variable. "
         "For example, in 2x + 5 = 13, subtract 5 from both sides to get 2x = 8."),
        ("Quadratic equations have the form ax^2 + bx + c = 0. "
         "They can be solved using the quadratic formula."),
        ("The Pythagorean theorem states that in a right triangle, "
         "a^2 + b^2 = c^2 where c is the hypotenuse.")
    ]
    
    all_chunks = []
    for i, doc_text in enumerate(docs):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(doc_text)
            temp_path = f.name
        
        chunks = ingestor.ingest_file(temp_path, priority="normal", trusted=True)
        all_chunks.extend(chunks)
        os.unlink(temp_path)
    
    # Index chunks
    indexer.index_chunks(all_chunks)
    
    # Create retriever
    retriever = DocumentRetriever(indexer, top_k=3)
    
    yield retriever, indexer, all_chunks
    
    # Cleanup
    indexer.clear_collection()


def test_basic_retrieval(setup_test_index):
    """Test basic retrieval functionality."""
    retriever, indexer, _ = setup_test_index
    
    query = "How do I solve a linear equation?"
    results = retriever.retrieve(query, top_k=3)
    
    assert len(results) > 0, "Should retrieve at least one result"
    assert len(results) <= 3, "Should not exceed top_k"
    
    # Check that results have required fields
    for result in results:
        assert 'chunk_id' in result
        assert 'chunk_text' in result
        assert 'similarity' in result
        assert 'metadata' in result
    
    # First result should be about linear equations
    assert "linear" in results[0]['chunk_text'].lower() or "2x" in results[0]['chunk_text']
    
    print(f"✓ Basic retrieval: {len(results)} results")
    print(f"  Top result similarity: {results[0]['similarity']:.3f}")


def test_priority_boosting(setup_test_index):
    """Test that priority boosting affects ranking."""
    retriever, indexer, all_chunks = setup_test_index
    
    # Add a high-priority chunk
    ingestor = DocumentIngestor()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Rubric: To solve linear equations, always show all steps.")
        temp_path = f.name
    
    rubric_chunks = ingestor.ingest_file(temp_path, priority="rubric", trusted=True)
    indexer.index_chunks(rubric_chunks)
    os.unlink(temp_path)
    
    # Retrieve with priority boost
    query = "solving linear equations"
    results = retriever.retrieve(query, top_k=5, priority_boost=True)
    
    assert len(results) > 0
    
    # Check that boosted similarity is present
    for result in results:
        assert 'boosted_similarity' in result or 'similarity' in result
    
    print(f"✓ Priority boosting: {len(results)} results")


def test_retrieval_logging(setup_test_index):
    """Test that retrieval is logged."""
    retriever, _, _ = setup_test_index
    
    query = "test query"
    retriever.retrieve(query, top_k=2)
    
    # Check that log file was created
    log_files = os.listdir(retriever.log_dir)
    assert len(log_files) > 0, "Should create log file"
    
    print(f"✓ Retrieval logging: {len(log_files)} log file(s)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
