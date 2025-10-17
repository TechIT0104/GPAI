"""
Test ingestion module.
"""

import pytest
import os
import tempfile
from backend.ingest import DocumentIngestor, extract_file_metadata


def test_text_file_ingestion():
    """Test ingesting a simple text file."""
    ingestor = DocumentIngestor(chunk_size=100, chunk_overlap=20)
    
    # Create temp text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document. " * 50)  # Repeat to get multiple chunks
        temp_path = f.name
    
    try:
        chunks = ingestor.ingest_file(temp_path, priority="normal", trusted=True)
        
        assert len(chunks) > 0, "Should create at least one chunk"
        assert all(chunk.filename == os.path.basename(temp_path) for chunk in chunks)
        assert all(chunk.file_type == "txt" for chunk in chunks)
        assert all(chunk.priority == "normal" for chunk in chunks)
        assert all(chunk.trusted for chunk in chunks)
        
        print(f"✓ Text ingestion: {len(chunks)} chunks created")
    finally:
        os.unlink(temp_path)


def test_chunking_with_overlap():
    """Test that chunking creates overlapping chunks."""
    ingestor = DocumentIngestor(chunk_size=50, chunk_overlap=10)
    
    text = "word " * 100  # 100 words
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text)
        temp_path = f.name
    
    try:
        chunks = ingestor.ingest_file(temp_path)
        
        assert len(chunks) >= 2, "Should create multiple chunks"
        
        # Check that chunks have reasonable token counts
        for chunk in chunks:
            assert chunk.token_count <= ingestor.chunk_size + 10  # Allow some tolerance
        
        print(f"✓ Chunking: {len(chunks)} chunks with overlap")
    finally:
        os.unlink(temp_path)


def test_file_metadata_extraction():
    """Test metadata extraction."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        metadata = extract_file_metadata(temp_path)
        
        assert 'filename' in metadata
        assert 'extension' in metadata
        assert 'size_bytes' in metadata
        assert metadata['extension'] == '.txt'
        
        print(f"✓ Metadata extraction: {metadata}")
    finally:
        os.unlink(temp_path)


def test_priority_and_trust_flags():
    """Test that priority and trust flags are preserved."""
    ingestor = DocumentIngestor()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Rubric content")
        temp_path = f.name
    
    try:
        chunks = ingestor.ingest_file(temp_path, priority="rubric", trusted=False)
        
        assert all(chunk.priority == "rubric" for chunk in chunks)
        assert all(not chunk.trusted for chunk in chunks)
        
        print(f"✓ Priority and trust flags preserved")
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
