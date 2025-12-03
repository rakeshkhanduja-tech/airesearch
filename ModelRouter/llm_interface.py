from abc import ABC, abstractmethod
import time
import random
from typing import Dict, Any
from config import LLMConfig

class BaseLLM(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, context: str = "") -> Dict[str, Any]:
        pass

class MockLLM(BaseLLM):
    def generate(self, prompt: str, context: str = "") -> Dict[str, Any]:
        # Simulate latency based on "power"
        latency = 0.5
        if "powerful" in self.config.model_id:
            latency = 2.0
        elif "fast" in self.config.model_id:
            latency = 0.2
        
        time.sleep(latency)
        
        response_text = f"[{self.config.name}] Response to: '{prompt}'"
        if context:
            response_text += f"\nContext used: {context[:50]}..."
            
        return {
            "text": response_text,
            "model": self.config.name,
            "tokens_used": len(prompt.split()) + len(response_text.split()),
            "cost": (len(prompt.split()) + len(response_text.split())) * self.config.cost_per_token
        }

class LLMFactory:
    @staticmethod
    def create_llm(config: LLMConfig) -> BaseLLM:
        if config.provider == "mock":
            return MockLLM(config)
        # Add real providers here later
        raise ValueError(f"Unsupported provider: {config.provider}")
