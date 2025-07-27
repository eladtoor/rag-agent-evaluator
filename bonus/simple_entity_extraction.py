import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import re
from datetime import datetime

class SimpleEntityExtractor:
    def __init__(self):
        """
        Initialize simple entity extractor
        """
        self.entities = []
        self.relationships = []
        
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
        Extract entities from text using pattern matching
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            List of extracted entities with metadata
        """
        entities = []
        
        # Extract person names
        person_pattern = r'\b(?:matt|kiera|ed|dave|sharris|jmalik|junaid malik)\b'
        persons = re.findall(person_pattern, text, re.IGNORECASE)
        
        # Extract system/technical entities
        system_pattern = r'\b(?:staging-3|corp-vpn3|corp-fs02|sw-07b|jenkins|buildconfig\.yaml|logi_loader\.dll|q2_pipeline|marketing_campaign_2020)\b'
        systems = re.findall(system_pattern, text, re.IGNORECASE)
        
        # Extract time references
        time_pattern = r'\b(?:monday|tuesday|wednesday|3:11 am|6:12 am|7:41 am|2:47 am|4:23 am|7:12 pm|10:30 pm|8:19 pm|9:02 pm)\b'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        
        # Extract locations/areas
        location_pattern = r'\b(?:west wing|third floor|sales area|marketing workstations|training pc|dev servers|lab servers)\b'
        locations = re.findall(location_pattern, text, re.IGNORECASE)
        
        # Extract malware/security entities
        security_pattern = r'\b(?:malware|antivirus|av console|heuristic scan|endpoint protection|vpn tunnel|dlp|breach|compromise)\b'
        security_entities = re.findall(security_pattern, text, re.IGNORECASE)
        
        # Extract network entities
        network_pattern = r'\b(?:subnet|vlan|wan|dns|smb|https|cdn\.nodeflux\.ai|updates-status-sync\.live|metrics\.windowupdate\.io)\b'
        network_entities = re.findall(network_pattern, text, re.IGNORECASE)
        
        # Create entity objects
        for person in set(persons):
            entities.append({
                "type": "PERSON",
                "value": person.title(),
                "confidence": 0.9,
                "count": persons.count(person)
            })
        
        for system in set(systems):
            entities.append({
                "type": "SYSTEM",
                "value": system,
                "confidence": 0.9,
                "count": systems.count(system)
            })
        
        for time in set(times):
            entities.append({
                "type": "TIME",
                "value": time,
                "confidence": 0.9,
                "count": times.count(time)
            })
        
        for location in set(locations):
            entities.append({
                "type": "LOCATION",
                "value": location,
                "confidence": 0.8,
                "count": locations.count(location)
            })
        
        for security in set(security_entities):
            entities.append({
                "type": "SECURITY",
                "value": security,
                "confidence": 0.8,
                "count": security_entities.count(security)
            })
        
        for network in set(network_entities):
            entities.append({
                "type": "NETWORK",
                "value": network,
                "confidence": 0.8,
                "count": network_entities.count(network)
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
        security = [e for e in entities if e["type"] == "SECURITY"]
        
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
        
        # Security relationships
        for sec in security:
            for system in systems:
                if sec["value"].lower() in ["malware", "antivirus", "av console"]:
                    relationships.append({
                        "source": sec["value"],
                        "target": system["value"],
                        "relationship_type": "PROTECTS",
                        "confidence": 0.6
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
                "extraction_method": "pattern_matching"
            },
            "entities": entities,
            "relationships": relationships
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {output_file}")
    
    def run_extraction(self, text_file_path: str, output_file: str = "simple_entities_results.json"):
        """
        Run the complete entity extraction process
        
        Args:
            text_file_path: Path to the input text file
            output_file: Path to the output JSON file
        """
        print("Starting simple entity extraction...")
        
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
        
        return entities, relationships

def main():
    """
    Main function to run the simple entity extraction
    """
    # Path to the text file
    text_file = Path(__file__).parent.parent / "The_Day_Everything_Slowed_Down.txt"
    output_file = Path(__file__).parent / "simple_entities_results.json"
    
    # Initialize extractor
    extractor = SimpleEntityExtractor()
    
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
        unique_values = list(set(values))
        print(f"{entity_type}: {len(unique_values)} unique entities")
        print(f"  Examples: {', '.join(unique_values[:5])}")
        if len(unique_values) > 5:
            print(f"  ... and {len(unique_values) - 5} more")
    
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