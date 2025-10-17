"""
Optional FastAPI endpoints for Resource-Scoped Mode.
Can be run separately from Streamlit for API access.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import tempfile
import os
from pydantic import BaseModel

from backend import (
    DocumentIngestor,
    EmbeddingIndexer,
    DocumentRetriever,
    LLMGenerator,
    StepValidator
)

app = FastAPI(
    title="Resource-Scoped Mode API",
    description="Document-grounded STEM problem solver API",
    version="1.0.0"
)

# Global state (in production, use proper session management)
_indexer = None
_retriever = None


class SolutionRequest(BaseModel):
    """Request model for solution generation."""
    question: str
    mode: str = "prefer"  # strict or prefer
    method_constraints: Optional[List[str]] = None
    top_k: int = 10


@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    priority: str = Form("normal"),
    trusted: bool = Form(True)
):
    """
    Upload and index documents.
    
    Args:
        files: List of files to upload
        priority: Priority level (rubric, slides, textbook, normal)
        trusted: Whether sources are trusted
        
    Returns:
        Upload status and indexing stats
    """
    global _indexer, _retriever
    
    try:
        # Initialize indexer if needed
        if _indexer is None:
            _indexer = EmbeddingIndexer(
                chroma_db_dir=os.getenv("CHROMA_DB_DIR", "./chroma_db")
            )
            _retriever = DocumentRetriever(_indexer)
        
        # Process files
        ingestor = DocumentIngestor(
            chunk_size=int(os.getenv("CHUNK_SIZE", 600)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 100))
        )
        
        all_chunks = []
        processed_files = []
        
        for file in files:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            # Ingest
            chunks = ingestor.ingest_file(tmp_path, priority=priority, trusted=trusted)
            all_chunks.extend(chunks)
            
            os.unlink(tmp_path)
            
            processed_files.append({
                "filename": file.filename,
                "chunks": len(chunks)
            })
        
        # Index
        indexed_count = _indexer.index_chunks(all_chunks)
        
        # Get stats
        stats = _indexer.get_collection_stats()
        
        return JSONResponse({
            "status": "success",
            "files_processed": len(files),
            "total_chunks": indexed_count,
            "details": processed_files,
            "collection_stats": stats
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/solve")
async def generate_solution(request: SolutionRequest):
    """
    Generate a solution for a question.
    
    Args:
        request: Solution request with question and settings
        
    Returns:
        Generated solution with validation results
    """
    global _indexer, _retriever
    
    if _retriever is None:
        raise HTTPException(status_code=400, detail="No documents uploaded. Upload files first via /upload")
    
    try:
        # Retrieve relevant chunks
        chunks = _retriever.retrieve(request.question, top_k=request.top_k)
        
        if not chunks:
            return JSONResponse({
                "status": "no_results",
                "message": "No relevant content found in uploaded resources"
            })
        
        # Generate solution
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
            generator = LLMGenerator(
                api_key=api_key,
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                provider="openai"
            )
        elif provider == "ollama":
            generator = LLMGenerator(
                model=os.getenv("OLLAMA_MODEL", "mistral"),
                provider="ollama",
                ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported LLM provider: {provider}")
        
        result = generator.generate_solution(
            question=request.question,
            retrieved_chunks=chunks,
            mode=request.mode,
            method_constraints=request.method_constraints
        )
        
        # Parse steps
        steps = generator.parse_solution_steps(result['solution'])
        
        # Validate
        validator = StepValidator()
        validation = validator.validate_solution(steps, chunks, mode=request.mode)
        
        # Format response
        if validation['status'] == "FAILED":
            return JSONResponse({
                "status": "failed",
                "mode": request.mode,
                "message": validation['message'],
                "refusal": "No supported solution found in resources."
            })
        
        return JSONResponse({
            "status": "success",
            "mode": request.mode,
            "question": request.question,
            "solution": result['solution'],
            "validation": {
                "status": validation['status'],
                "message": validation['message'],
                "total_steps": validation['total_steps'],
                "supported_steps": validation['supported_steps'],
                "steps": validation['step_validations']
            },
            "chunks_used": len(chunks),
            "model": result['model']
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get API status and collection info."""
    global _indexer
    
    if _indexer is None:
        return JSONResponse({
            "status": "not_initialized",
            "message": "No documents indexed yet"
        })
    
    stats = _indexer.get_collection_stats()
    
    return JSONResponse({
        "status": "ready",
        "collection": stats
    })


@app.delete("/clear")
async def clear_collection():
    """Clear all indexed documents."""
    global _indexer, _retriever
    
    if _indexer is None:
        return JSONResponse({"status": "already_empty"})
    
    _indexer.clear_collection()
    
    return JSONResponse({
        "status": "success",
        "message": "All documents cleared"
    })


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Resource-Scoped Mode API",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload": "Upload and index documents",
            "POST /solve": "Generate solution for a question",
            "GET /status": "Get API status",
            "DELETE /clear": "Clear all documents",
            "GET /docs": "Interactive API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
