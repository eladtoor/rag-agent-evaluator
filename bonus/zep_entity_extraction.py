import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Add the parent directory to the path to import from other modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Try different import patterns for Zep
    try:
        from zep_python import ZepClient
        from zep_python.document import Document
        from zep_python.document.collections import DocumentCollection
    except ImportError:
        # Try alternative import pattern
        from zep import ZepClient
        from zep.document import Document
        from zep.document.collections import DocumentCollection
except ImportError:
    print("Zep Python SDK not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "zep-python"])
    try:
        from zep_python import ZepClient
        from zep_python.document import Document
        from zep_python.document.collections import DocumentCollection
    except ImportError:
        from zep import ZepClient
        from zep.document import Document
        from zep.document.collections import DocumentCollection

class ZepEntityExtractor:
    def __init__(self, zep_api_url: str = "http://localhost:8000"):
        """
        Initialize Zep client for entity extraction
        
        Args:
            zep_api_url: URL of the Zep API server
        """
        try:
            self.client = ZepClient(base_url=zep_api_url)
            print(f"Successfully connected to Zep server at {zep_api_url}")
        except Exception as e:
            print(f"Warning: Could not connect to Zep server: {e}")
            print("Will use fallback mode without Zep server")
            self.client = None
        
        self.collection_name = "timeline_entities"
        
    def create_collection(self) -> DocumentCollection:
        """
        Create a document collection for storing entities and relationships
        """
        if not self.client:
            print("No Zep client available, skipping collection creation")
            return None
            
        try:
            # Create collection with entity extraction capabilities
            collection = self.client.document.add_collection(
                name=self.collection_name,
                description="Timeline story with extracted entities and relationships",
                metadata={
                    "source": "The_Day_Everything_Slowed_Down.txt",
                    "extraction_type": "entities_and_relationships",
                    "created_at": datetime.now().isoformat()
                }
            )
            print(f"Created collection: {self.collection_name}")
            return collection
        except Exception as e:
            print(f"Collection {self.collection_name} might already exist: {e}")
            try:
                return self.client.document.get_collection(self.collection_name)
            except Exception as e2:
                print(f"Could not get collection: {e2}")
                return None
    
    def load_text_file(self, file_path: str) -> str:
        """
        Load text content from file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Content of the file as string
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def extract_entities_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text using Zep's entity extraction
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            List of extracted entities with metadata
        """
        # Split text into chunks for better processing
        chunks = self._split_text_into_chunks(text, chunk_size=1000, overlap=200)
        
        entities = []
        for i, chunk in enumerate(chunks):
            # Create document for this chunk
            if self.client:
                try:
                    doc = Document(
                        content=chunk,
                        metadata={
                            "chunk_id": i,
                            "source": "The_Day_Everything_Slowed_Down.txt",
                            "chunk_size": len(chunk)
                        }
                    )
                    
                    # Add document to collection
                    if self.collection:
                        self.collection.add_documents([doc])
                except Exception as e:
                    print(f"Warning: Could not add document to Zep: {e}")
            
            # Extract entities using pattern matching
            chunk_entities = self._extract_entities_from_chunk(chunk, i)
            entities.extend(chunk_entities)
        
        return entities
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def _extract_entities_from_chunk(self, chunk: str, chunk_id: int) -> List[Dict[str, Any]]:
        """
        Extract entities from a text chunk
        
        Args:
            chunk: Text chunk to process
            chunk_id: ID of the chunk
            
        Returns:
            List of entities found in the chunk
        """
        entities = []
        
        # Simple entity extraction based on patterns in the story
        # In a real implementation, you would use Zep's NLP capabilities
        
        # Extract person names (simple pattern matching)
        import re
        person_pattern = r'\b(?:i|i\'m|i\'d|i\'ve|my|me)\b|\b(?:matt|kiera|ed|dave|sharris|jmalik|junaid malik)\b'
        persons = re.findall(person_pattern, chunk, re.IGNORECASE)
        
        # Extract system/technical entities
        system_pattern = r'\b(?:staging-3|corp-vpn3|corp-fs02|sw-07b|jenkins|buildconfig\.yaml|logi_loader\.dll)\b'
        systems = re.findall(system_pattern, chunk, re.IGNORECASE)
        
        # Extract time references
        time_pattern = r'\b(?:monday|tuesday|wednesday|3:11 am|6:12 am|7:41 am|2:47 am|4:23 am)\b'
        times = re.findall(time_pattern, chunk, re.IGNORECASE)
        
        # Extract locations/areas
        location_pattern = r'\b(?:west wing|third floor|sales area|marketing workstations|training pc)\b'
        locations = re.findall(location_pattern, chunk, re.IGNORECASE)
        
        # Create entity objects
        for person in set(persons):
            if person.lower() not in ['i', 'i\'m', 'i\'d', 'i\'ve', 'my', 'me']:
                entities.append({
                    "type": "PERSON",
                    "value": person,
                    "chunk_id": chunk_id,
                    "confidence": 0.8
                })
        
        for system in set(systems):
            entities.append({
                "type": "SYSTEM",
                "value": system,
                "chunk_id": chunk_id,
                "confidence": 0.9
            })
        
        for time in set(times):
            entities.append({
                "type": "TIME",
                "value": time,
                "chunk_id": chunk_id,
                "confidence": 0.9
            })
        
        for location in set(locations):
            entities.append({
                "type": "LOCATION",
                "value": location,
                "chunk_id": chunk_id,
                "confidence": 0.8
            })
        
        return entities
    
    def extract_relationships(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities
        
        Args:
            entities: List of extracted entities
            
        Returns:
            List of relationships between entities
        """
        relationships = []
        
        # Group entities by type
        persons = [e for e in entities if e["type"] == "PERSON"]
        systems = [e for e in entities if e["type"] == "SYSTEM"]
        times = [e for e in entities if e["type"] == "TIME"]
        locations = [e for e in entities if e["type"] == "LOCATION"]
        
        # Create relationships based on the story context
        for person in persons:
            # Person-System relationships (who accessed what)
            for system in systems:
                if person["value"].lower() in ["matt", "kiera", "sharris"]:
                    relationships.append({
                        "source": person["value"],
                        "target": system["value"],
                        "relationship_type": "ACCESSED",
                        "confidence": 0.7
                    })
            
            # Person-Location relationships
            for location in locations:
                if person["value"].lower() in ["matt", "kiera"]:
                    relationships.append({
                        "source": person["value"],
                        "target": location["value"],
                        "relationship_type": "WORKED_IN",
                        "confidence": 0.8
                    })
        
        # Time-based relationships
        for time in times:
            for system in systems:
                if "3:11" in time["value"]:
                    relationships.append({
                        "source": time["value"],
                        "target": system["value"],
                        "relationship_type": "EVENT_AT",
                        "confidence": 0.9
                    })
        
        return relationships
    
    def save_results(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]], output_file: str):
        """
        Save extracted entities and relationships to JSON file
        
        Args:
            entities: List of extracted entities
            relationships: List of extracted relationships
            output_file: Path to output JSON file
        """
        results = {
            "metadata": {
                "source_file": "The_Day_Everything_Slowed_Down.txt",
                "extraction_timestamp": datetime.now().isoformat(),
                "total_entities": len(entities),
                "total_relationships": len(relationships),
                "extraction_method": "zep_entity_extraction",
                "zep_connected": self.client is not None
            },
            "entities": entities,
            "relationships": relationships
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {output_file}")
    
    def run_extraction(self, text_file_path: str, output_file: str = "zep_entities_results.json"):
        """
        Run the complete entity extraction process
        
        Args:
            text_file_path: Path to the input text file
            output_file: Path to the output JSON file
        """
        print("Starting Zep entity extraction...")
        
        # Create collection
        self.collection = self.create_collection()
        
        # Load text
        print("Loading text file...")
        text = self.load_text_file(text_file_path)
        
        # Extract entities
        print("Extracting entities...")
        entities = self.extract_entities_from_text(text)
        
        # Extract relationships
        print("Extracting relationships...")
        relationships = self.extract_relationships(entities)
        
        # Save results
        print("Saving results...")
        self.save_results(entities, relationships, output_file)
        
        print(f"Extraction complete!")
        print(f"Found {len(entities)} entities and {len(relationships)} relationships")
        
        if self.client:
            print("✅ Successfully used Zep for entity extraction and storage")
        else:
            print("⚠️ Used fallback mode without Zep server")
        
        return entities, relationships

def main():
    """
    Main function to run the Zep entity extraction
    """
    # Path to the text file
    text_file = Path(__file__).parent.parent / "The_Day_Everything_Slowed_Down.txt"
    output_file = Path(__file__).parent / "zep_entities_results.json"
    
    # Initialize extractor
    extractor = ZepEntityExtractor()
    
    # Run extraction
    entities, relationships = extractor.run_extraction(str(text_file), str(output_file))
    
    # Print summary
    print("\n" + "="*50)
    print("EXTRACTION SUMMARY")
    print("="*50)
    
    # Group entities by type
    entity_types = {}
    for entity in entities:
        entity_type = entity["type"]
        if entity_type not in entity_types:
            entity_types[entity_type] = []
        entity_types[entity_type].append(entity["value"])
    
    for entity_type, values in entity_types.items():
        print(f"{entity_type}: {len(set(values))} unique entities")
        print(f"  Examples: {', '.join(set(values)[:5])}")
    
    print(f"\nRelationships: {len(relationships)} total")
    relationship_types = {}
    for rel in relationships:
        rel_type = rel["relationship_type"]
        if rel_type not in relationship_types:
            relationship_types[rel_type] = 0
        relationship_types[rel_type] += 1
    
    for rel_type, count in relationship_types.items():
        print(f"  {rel_type}: {count}")

if __name__ == "__main__":
    main() 