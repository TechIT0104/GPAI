"""
Retrieval module with ranking and metadata extraction.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.embed_and_index import EmbeddingIndexer


class DocumentRetriever:
    """Handles retrieval and ranking of document chunks."""
    
    def __init__(
        self,
        indexer: EmbeddingIndexer,
        top_k: int = 10,
        log_dir: str = "./logs"
    ):
        """
        Initialize retriever.
        
        Args:
            indexer: EmbeddingIndexer instance
            top_k: Number of top chunks to retrieve
            log_dir: Directory for retrieval logs
        """
        self.indexer = indexer
        self.top_k = top_k
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        priority_boost: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Query text
            top_k: Number of results (overrides default)
            filter_metadata: Optional metadata filters
            priority_boost: Whether to boost high-priority documents
            
        Returns:
            List of retrieved chunks with metadata and scores
        """
        k = top_k if top_k is not None else self.top_k
        
        # Query the collection
        results = self.indexer.collection.query(
            query_texts=[query],
            n_results=k * 2 if priority_boost else k,  # Get more for reranking
            where=filter_metadata
        )
        
        # Process results
        retrieved_chunks = []
        
        if results and results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                chunk_data = {
                    "chunk_id": results['ids'][0][i],
                    "chunk_text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else 0.0,
                    "similarity": 1.0 - results['distances'][0][i] if 'distances' in results else 1.0,
                    "rank": i
                }
                retrieved_chunks.append(chunk_data)
        
        # Apply priority boosting if enabled
        if priority_boost and retrieved_chunks:
            retrieved_chunks = self._apply_priority_boost(retrieved_chunks)
        
        # Limit to top_k
        retrieved_chunks = retrieved_chunks[:k]
        
        # Log retrieval
        self._log_retrieval(query, retrieved_chunks, filter_metadata)
        
        return retrieved_chunks
    
    def _apply_priority_boost(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank chunks based on priority and trust.
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Reranked chunks
        """
        priority_weights = {
            "rubric": 1.3,
            "slides": 1.2,
            "textbook": 1.1,
            "normal": 1.0
        }
        
        # Calculate boosted scores
        for chunk in chunks:
            metadata = chunk['metadata']
            priority = metadata.get('priority', 'normal')
            trusted = metadata.get('trusted', True)
            
            # Apply priority weight
            boost = priority_weights.get(priority, 1.0)
            
            # Apply trust boost
            if trusted:
                boost *= 1.1
            
            # Calculate boosted similarity
            chunk['boosted_similarity'] = chunk['similarity'] * boost
            chunk['priority_boost'] = boost
        
        # Sort by boosted similarity
        chunks.sort(key=lambda x: x['boosted_similarity'], reverse=True)
        
        # Update ranks
        for i, chunk in enumerate(chunks):
            chunk['rank'] = i
        
        return chunks
    
    def retrieve_by_page(
        self,
        filename: str,
        page: int,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks from a specific page.
        
        Args:
            filename: Name of the file
            page: Page number
            query: Optional query for relevance ranking
            
        Returns:
            List of chunks from the specified page
        """
        # Get all chunks from this page
        results = self.indexer.collection.get(
            where={
                "$and": [
                    {"filename": filename},
                    {"page": page}
                ]
            }
        )
        
        chunks = []
        
        if results and results['ids']:
            for i in range(len(results['ids'])):
                chunk_data = {
                    "chunk_id": results['ids'][i],
                    "chunk_text": results['documents'][i],
                    "metadata": results['metadatas'][i],
                    "similarity": 1.0,
                    "rank": i
                }
                chunks.append(chunk_data)
        
        # If query provided, rerank by relevance
        if query and chunks:
            query_embedding = self.indexer.embed_text(query)
            
            # Calculate similarities
            for chunk in chunks:
                chunk_embedding = self.indexer.embed_text(chunk['chunk_text'])
                similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                chunk['similarity'] = similarity
            
            chunks.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Update ranks
            for i, chunk in enumerate(chunks):
                chunk['rank'] = i
        
        return chunks
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        
        if norm_product == 0:
            return 0.0
        
        return float(dot_product / norm_product)
    
    def _log_retrieval(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None
    ):
        """
        Log retrieval operation for audit.
        
        Args:
            query: The query
            chunks: Retrieved chunks
            filters: Applied filters
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "top_k": len(chunks),
            "filters": filters,
            "results": [
                {
                    "rank": chunk['rank'],
                    "chunk_id": chunk['chunk_id'],
                    "similarity": chunk.get('similarity', 0.0),
                    "boosted_similarity": chunk.get('boosted_similarity', chunk.get('similarity', 0.0)),
                    "filename": chunk['metadata'].get('filename'),
                    "page": chunk['metadata'].get('page'),
                    "priority": chunk['metadata'].get('priority'),
                    "trusted": chunk['metadata'].get('trusted')
                }
                for chunk in chunks
            ]
        }
        
        # Save to log file
        log_filename = f"retrieval_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        log_path = os.path.join(self.log_dir, log_filename)
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_context_window(
        self,
        chunk_id: str,
        window_size: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get surrounding chunks for context.
        
        Args:
            chunk_id: ID of the central chunk
            window_size: Number of chunks before/after to include
            
        Returns:
            List of chunks including context
        """
        # Parse chunk_id to get file and chunk index
        # Format: filename_pPAGE_cINDEX
        parts = chunk_id.split('_c')
        if len(parts) != 2:
            return []
        
        base = parts[0]
        chunk_index = int(parts[1])
        
        # Get adjacent chunks
        adjacent_ids = []
        for offset in range(-window_size, window_size + 1):
            if offset == 0:
                adjacent_ids.append(chunk_id)
            else:
                new_index = chunk_index + offset
                if new_index >= 0:
                    adjacent_ids.append(f"{base}_c{new_index}")
        
        # Fetch chunks
        try:
            results = self.indexer.collection.get(ids=adjacent_ids)
            
            chunks = []
            if results and results['ids']:
                for i in range(len(results['ids'])):
                    chunk_data = {
                        "chunk_id": results['ids'][i],
                        "chunk_text": results['documents'][i],
                        "metadata": results['metadatas'][i],
                        "rank": i
                    }
                    chunks.append(chunk_data)
            
            return chunks
        except Exception as e:
            print(f"Error getting context window: {e}")
            return []


def format_retrieved_chunks(chunks: List[Dict[str, Any]], max_length: int = 8000) -> str:
    """
    Format retrieved chunks for LLM input.
    
    Args:
        chunks: List of retrieved chunks
        max_length: Maximum total character length
        
    Returns:
        Formatted string
    """
    formatted = []
    total_length = 0
    
    for chunk in chunks:
        metadata = chunk['metadata']
        chunk_text = chunk['chunk_text']
        
        # Format: [doc:filename | p:page | chunk:id] text
        citation = f"[doc:{metadata.get('filename', 'unknown')} | p:{metadata.get('page', 0)} | chunk:{chunk['chunk_id']}]"
        
        entry = f"{citation}\n{chunk_text}\n"
        
        if total_length + len(entry) > max_length:
            break
        
        formatted.append(entry)
        total_length += len(entry)
    
    return "\n---\n".join(formatted)
