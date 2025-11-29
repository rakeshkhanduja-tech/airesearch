from typing import Any, Dict
from mind360.core.input_layer import InputLayer
from mind360.core.parser import Parser
from mind360.core.normalizer import Normalizer
from mind360.core.node_generator import NodeGenerator
from mind360.core.relationship_builder import RelationshipBuilder
from mind360.storage.smg_store import SMGStore

class Mind360SDK:
    """
    Main entry point for the Mind360 SDK.
    """
    def __init__(self, neo4j_uri: str = None, neo4j_user: str = None, neo4j_password: str = None):
        self.input_layer = InputLayer()
        self.parser = Parser()
        self.normalizer = Normalizer()
        self.node_generator = NodeGenerator()
        self.relationship_builder = RelationshipBuilder()
        self.store = SMGStore(neo4j_uri, neo4j_user, neo4j_password)

    def process_memory(self, input_data: Any) -> Dict[str, Any]:
        """
        Processes input data through the SMG pipeline and stores it.
        
        Args:
            input_data: The raw input data.
            
        Returns:
            A summary of the operation.
        """
        # 1. Input
        ingested = self.input_layer.ingest(input_data)
        
        # 2. Parse
        parsed = self.parser.parse(ingested)
        
        # 3. Normalize
        normalized = self.normalizer.normalize(parsed)
        
        # 4. Generate Nodes
        nodes = self.node_generator.generate_nodes(normalized)
        
        # 5. Build Relationships
        relationships = self.relationship_builder.build_relationships(nodes)
        
        # 6. Store
        try:
            self.store.store_graph(nodes, relationships)
            storage_status = "success"
        except Exception as e:
            storage_status = f"failed: {str(e)}"
            
        return {
            "status": "processed",
            "nodes_generated": len(nodes),
            "relationships_built": len(relationships),
            "storage_status": storage_status
        }
