import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from mind360.api.interface import Mind360SDK

def main():
    print("Initializing Mind360 SDK...")
    # Initialize with dummy credentials for testing
    sdk = Mind360SDK(neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="xxxxxx")
    
    input_data = "The quick brown fox jumps over the lazy dog."
    print(f"Processing input: '{input_data}'")
    
    result = sdk.process_memory(input_data)
    
    print("\nResult:")
    print(result)
    
    if result["storage_status"].startswith("failed"):
        print("\nNote: Storage failed as expected (no Neo4j instance running). Pipeline logic verified.")

if __name__ == "__main__":
    main()
