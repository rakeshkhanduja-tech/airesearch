import json
import os
from typing import List, Optional
from pydantic import BaseModel

class LLMConfig(BaseModel):
    name: str
    provider: str  # e.g., "mock", "openai", "anthropic"
    model_id: str
    cost_per_token: float
    capabilities: List[str]  # e.g., ["coding", "creative", "reasoning"]
    api_key: Optional[str] = None
    endpoint: Optional[str] = None

class VectorDBConfig(BaseModel):
    path: str = "./chroma_db"
    collection_name: str = "model_router_context"

class AppConfig(BaseModel):
    llms: List[LLMConfig]
    vector_db: VectorDBConfig

class ConfigLoader:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path

    def load_config(self) -> AppConfig:
        if not os.path.exists(self.config_path):
            # Return default mock config if file doesn't exist
            return self._get_mock_config()
        
        with open(self.config_path, "r") as f:
            data = json.load(f)
        return AppConfig(**data)

    def _get_mock_config(self) -> AppConfig:
        return AppConfig(
            llms=[
                LLMConfig(name="FastMock", provider="mock", model_id="mock-fast", cost_per_token=0.0001, capabilities=["general"]),
                LLMConfig(name="PowerfulMock", provider="mock", model_id="mock-powerful", cost_per_token=0.002, capabilities=["reasoning", "coding"]),
                LLMConfig(name="CheapMock", provider="mock", model_id="mock-cheap", cost_per_token=0.00005, capabilities=["general"]),
                LLMConfig(name="CodeMock", provider="mock", model_id="mock-code", cost_per_token=0.001, capabilities=["coding"]),
                LLMConfig(name="CreativeMock", provider="mock", model_id="mock-creative", cost_per_token=0.0015, capabilities=["creative"]),
            ],
            vector_db=VectorDBConfig()
        )

# Global config instance
config_loader = ConfigLoader()
app_config = config_loader.load_config()
