import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
import hashlib
from config import VectorDBConfig

class MemoryCache:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.order: List[str] = []

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            # Move to end (most recently used)
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None

    def put(self, key: str, value: Dict[str, Any]):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used
            oldest = self.order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.order.append(key)

class VectorStore:
    def __init__(self, config: VectorDBConfig):
        self.client = chromadb.PersistentClient(path=config.path)
        self.collection = self.client.get_or_create_collection(name=config.collection_name)

    def _hash_query(self, query: str) -> str:
        return hashlib.sha256(query.encode()).hexdigest()

    def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        query_hash = self._hash_query(query)
        results = self.collection.query(
            query_texts=[query],
            n_results=1,
            where={"type": "response_cache"}
        )
        
        if results['documents'] and results['documents'][0]:
            # Check if the retrieved document is actually a match for the query
            # For strict caching, we might want to check exact match or very high similarity
            # Here we rely on the vector similarity, but we should double check if it's the same query
            # Storing the query hash in metadata allows exact match check
            metadata = results['metadatas'][0][0]
            if metadata.get('query_hash') == query_hash:
                 return json.loads(results['documents'][0][0])
        return None

    def cache_response(self, query: str, response: Dict[str, Any]):
        query_hash = self._hash_query(query)
        self.collection.add(
            documents=[json.dumps(response)],
            metadatas=[{"type": "response_cache", "query_hash": query_hash}],
            ids=[query_hash]
        )

    def add_context(self, text: str, metadata: Dict[str, Any]):
        doc_id = hashlib.sha256(text.encode()).hexdigest()
        metadata["type"] = "context"
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def get_context(self, query: str, n_results: int = 2) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"type": "context"}
        )
        if results['documents']:
            return results['documents'][0]
        return []
