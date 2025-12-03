from typing import Dict, Any, List
from config import AppConfig, LLMConfig
from storage import MemoryCache, VectorStore
from llm_interface import LLMFactory

class RouterEngine:
    def __init__(self, config: AppConfig):
        self.config = config
        self.memory_cache = MemoryCache()
        self.vector_store = VectorStore(config.vector_db)
        self.llms = {cfg.name: LLMFactory.create_llm(cfg) for cfg in config.llms}

    def _analyze_query(self, query: str) -> List[str]:
        # Simple keyword-based categorization for mock purposes
        categories = []
        query_lower = query.lower()
        if "code" in query_lower or "function" in query_lower or "python" in query_lower:
            categories.append("coding")
        if "create" in query_lower or "write" in query_lower or "story" in query_lower:
            categories.append("creative")
        if "why" in query_lower or "how" in query_lower or "explain" in query_lower:
            categories.append("reasoning")
        
        if not categories:
            categories.append("general")
        return categories

    def _select_llm(self, categories: List[str]) -> str:
        # Scoring system to find best LLM
        best_llm = None
        best_score = -1
        
        for llm_config in self.config.llms:
            score = 0
            # Capability match
            for cat in categories:
                if cat in llm_config.capabilities:
                    score += 10
            
            # Cost preference (lower cost is better tie-breaker)
            score -= llm_config.cost_per_token * 1000 
            
            if score > best_score:
                best_score = score
                best_llm = llm_config.name
                
        return best_llm

    def process_query(self, query: str) -> Dict[str, Any]:
        # 1. Check Memory Cache
        cached_response = self.memory_cache.get(query)
        if cached_response:
            cached_response["source"] = "Memory Cache"
            cached_response["cost_saved"] = cached_response.get("cost", 0)
            return cached_response

        # 2. Check Persistent Cache (Vector DB)
        persistent_response = self.vector_store.get_cached_response(query)
        if persistent_response:
            # Update Memory Cache
            self.memory_cache.put(query, persistent_response)
            persistent_response["source"] = "Persistent Cache"
            persistent_response["cost_saved"] = persistent_response.get("cost", 0)
            return persistent_response

        # 3. Retrieve Context
        context_list = self.vector_store.get_context(query)
        context = "\n".join(context_list)

        # 4. Analyze Query & Route
        categories = self._analyze_query(query)
        selected_llm_name = self._select_llm(categories)
        llm = self.llms[selected_llm_name]

        # 5. Generate Response
        response = llm.generate(query, context)
        
        # Add metadata
        response["source"] = f"LLM ({selected_llm_name})"
        response["categories"] = categories
        
        # 6. Cache Response
        self.memory_cache.put(query, response)
        self.vector_store.cache_response(query, response)

        return response

    def add_knowledge(self, text: str, metadata: Dict[str, Any] = {}):
        self.vector_store.add_context(text, metadata)
