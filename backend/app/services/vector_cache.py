
"""Vector Cache module for the application.

This module provides functionality related to vector cache.
"""
from typing import Dict, List, Any, Optional, Tuple
import time
from threading import Lock

import numpy as np
class VectorCache:
    """In-memory cache for vector embeddings to improve search performance"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VectorCache, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """Initialize the cache"""
        self.document_embeddings: Dict[str, np.ndarray] = {}
        self.query_embeddings: Dict[str, np.ndarray] = {}
        self.document_metadata: Dict[str, Dict[str, Any]] = {}
        self.last_accessed: Dict[str, float] = {}
        self.max_cache_size = 1000  # Maximum number of vectors to cache
        self.ttl = 3600  # Time to live in seconds (1 hour)

    def get_document_embedding(self, doc_id: str) -> Optional[np.ndarray]:
        """Get document embedding from cache"""
        if doc_id in self.document_embeddings:
            self.last_accessed[doc_id] = time.time()
            return self.document_embeddings[doc_id]
        return None

    def get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Get query embedding from cache"""
        if query in self.query_embeddings:
            self.last_accessed[query] = time.time()
            return self.query_embeddings[query]
        return None

    def get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata from cache"""
        if doc_id in self.document_metadata:
            self.last_accessed[doc_id] = time.time()
            return self.document_metadata[doc_id]
        return None

    def store_document_embedding(
        self, doc_id: str, embedding: np.ndarray, metadata: Optional[Dict[str, Any]] = None):
        """Store document embedding in cache"""
        self._evict_if_needed()
        self.document_embeddings[doc_id] = embedding
        if metadata:
            self.document_metadata[doc_id] = metadata
        self.last_accessed[doc_id] = time.time()

    def store_document_metadata(self, doc_id: str, metadata: Dict[str, Any]):
        """Store document metadata in cache"""
        self._evict_if_needed()
        self.document_metadata[doc_id] = metadata
        self.last_accessed[doc_id] = time.time()

    def store_query_embedding(self, query: str, embedding: np.ndarray):
        """Store query embedding in cache"""
        self._evict_if_needed()
        self.query_embeddings[query] = embedding
        self.last_accessed[query] = time.time()

    def invalidate(self, doc_id: str):
        """Invalidate cache entry"""
        if doc_id in self.document_embeddings:
            del self.document_embeddings[doc_id]
        if doc_id in self.document_metadata:
            del self.document_metadata[doc_id]
        if doc_id in self.last_accessed:
            del self.last_accessed[doc_id]

    def clear(self):
        """Clear the entire cache"""
        self.document_embeddings.clear()
        self.query_embeddings.clear()
        self.document_metadata.clear()
        self.last_accessed.clear()

    def _evict_if_needed(self):
        """Evict least recently used items if cache is full"""
        # Evict expired items
        current_time = time.time()
        expired_keys = [k for k, v in self.last_accessed.items() if current_time - v > self.ttl]
        for key in expired_keys:
            self.invalidate(key)

        # If still too many items, evict least recently used
        if len(self.document_embeddings) + len(self.query_embeddings) >= self.max_cache_size:
            # Sort by last accessed time
            sorted_keys = sorted(self.last_accessed.items(), key=lambda x: x[1])
            # Remove oldest 10% of items
            num_to_remove = max(1, int(0.1 * len(sorted_keys)))
            for i in range(num_to_remove):
                if i < len(sorted_keys):
                    self.invalidate(sorted_keys[i][0])

    def find_similar_vectors(
        self, query_embedding: np.ndarray, limit: int = 10) -> List[Tuple[str, float]]:
        """Find similar vectors in cache using cosine similarity"""
        if not self.document_embeddings:
            return []

        results = []
        for doc_id, embedding in self.document_embeddings.items():
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            results.append((doc_id, similarity))

        # Sort by similarity (highest first) and return top k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
