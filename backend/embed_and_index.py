"""
Embedding and indexing module using sentence-transformers and ChromaDB.
"""

import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np
from backend.ingest import DocumentChunk


class EmbeddingIndexer:
    """Handles document embedding and vector database indexing."""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chroma_db_dir: str = "./chroma_db",
        collection_name: str = "resource_scoped_docs",
        use_openai: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize embedding and indexing components.
        
        Args:
            embedding_model: Model name for sentence-transformers or "openai"
            chroma_db_dir: Directory for ChromaDB storage
            collection_name: Name of the collection
            use_openai: Whether to use OpenAI embeddings
            openai_api_key: OpenAI API key if using OpenAI embeddings
        """
        self.use_openai = use_openai
        
        # Initialize embedding model
        if use_openai and openai_api_key:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=openai_api_key)
            self.embedding_model_name = "text-embedding-ada-002"
            self.encoder = None
            print(f"✓ Using OpenAI embeddings: {self.embedding_model_name}")
        else:
            self.encoder = SentenceTransformer(embedding_model)
            self.embedding_model_name = embedding_model
            print(f"✓ Using sentence-transformers: {embedding_model}")
        
        # Initialize ChromaDB
        os.makedirs(chroma_db_dir, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_db_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection_name = collection_name
        self.collection = None
        self._initialize_collection()
        
        print(f"✓ ChromaDB initialized at {chroma_db_dir}")
    
    def _initialize_collection(self):
        """Initialize or get existing collection."""
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"✓ Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Resource-scoped document chunks"}
            )
            print(f"✓ Created new collection: {self.collection_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if self.use_openai:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model_name
            )
            return response.data[0].embedding
        else:
            return self.encoder.encode(text, convert_to_numpy=True).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.use_openai:
            response = self.openai_client.embeddings.create(
                input=texts,
                model=self.embedding_model_name
            )
            return [item.embedding for item in response.data]
        else:
            embeddings = self.encoder.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
    
    def index_chunks(self, chunks: List[DocumentChunk], batch_size: int = 100) -> int:
        """
        Index document chunks into ChromaDB.
        
        Args:
            chunks: List of DocumentChunk objects
            batch_size: Number of chunks to process at once
            
        Returns:
            Number of chunks indexed
        """
        if not chunks:
            return 0
        
        indexed_count = 0
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Extract data
            chunk_ids = [chunk.chunk_id for chunk in batch]
            texts = [chunk.chunk_text for chunk in batch]
            
            # Generate embeddings
            embeddings = self.embed_batch(texts)
            
            # Prepare metadata
            metadatas = []
            for chunk in batch:
                metadata = {
                    "filename": chunk.filename,
                    "page": chunk.page,
                    "chunk_index": chunk.chunk_index,
                    "file_type": chunk.file_type,
                    "priority": chunk.priority,
                    "trusted": chunk.trusted,
                    "token_count": chunk.token_count,
                }
                # Add custom metadata if present
                if chunk.metadata:
                    for key, value in chunk.metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            metadata[f"meta_{key}"] = value
                
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            indexed_count += len(batch)
            print(f"Indexed {indexed_count}/{len(chunks)} chunks...")
        
        return indexed_count
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self._initialize_collection()
            print(f"✓ Collection cleared: {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the indexed collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample to analyze
            if count > 0:
                sample = self.collection.get(limit=min(10, count))
                
                # Analyze file types and priorities
                file_types = {}
                priorities = {}
                
                for metadata in sample.get('metadatas', []):
                    ft = metadata.get('file_type', 'unknown')
                    pr = metadata.get('priority', 'normal')
                    
                    file_types[ft] = file_types.get(ft, 0) + 1
                    priorities[pr] = priorities.get(pr, 0) + 1
                
                return {
                    "total_chunks": count,
                    "file_types": file_types,
                    "priorities": priorities,
                    "collection_name": self.collection_name,
                    "embedding_model": self.embedding_model_name
                }
            else:
                return {
                    "total_chunks": 0,
                    "collection_name": self.collection_name,
                    "embedding_model": self.embedding_model_name
                }
        except Exception as e:
            return {"error": str(e)}
    
    def delete_by_filename(self, filename: str) -> int:
        """
        Delete all chunks from a specific file.
        
        Args:
            filename: Name of file to remove
            
        Returns:
            Number of chunks deleted
        """
        try:
            # Query for chunks from this file
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                return len(results['ids'])
            return 0
        except Exception as e:
            print(f"Error deleting chunks for {filename}: {e}")
            return 0


def create_faiss_index(chunks: List[DocumentChunk], embedding_model: str = "all-MiniLM-L6-v2"):
    """
    Alternative indexing using FAISS (fallback option).
    
    Args:
        chunks: List of DocumentChunk objects
        embedding_model: Model name for embeddings
        
    Returns:
        Tuple of (faiss_index, chunk_metadata_list)
    """
    import faiss
    
    encoder = SentenceTransformer(embedding_model)
    texts = [chunk.chunk_text for chunk in chunks]
    
    # Generate embeddings
    embeddings = encoder.encode(texts, convert_to_numpy=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    # Store metadata separately
    metadata = [{
        "chunk_id": chunk.chunk_id,
        "filename": chunk.filename,
        "page": chunk.page,
        "chunk_text": chunk.chunk_text,
        "priority": chunk.priority,
        "trusted": chunk.trusted
    } for chunk in chunks]
    
    print(f"✓ FAISS index created with {len(chunks)} chunks")
    return index, metadata
