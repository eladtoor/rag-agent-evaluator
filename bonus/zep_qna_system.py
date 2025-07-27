import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from datetime import datetime

try:
    # Try different import patterns for Zep
    try:
        from zep_python import ZepClient
        from zep_python.document import Document
        from zep_python.document.collections import DocumentCollection
        from zep_python.memory import Memory
        from zep_python.user import User
    except ImportError:
        # Try alternative import pattern
        from zep import ZepClient
        from zep.document import Document
        from zep.document.collections import DocumentCollection
        from zep.memory import Memory
        from zep.user import User
except ImportError:
    print("Zep Python SDK not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "zep-python"])
    try:
        from zep_python import ZepClient
        from zep_python.document import Document
        from zep_python.document.collections import DocumentCollection
        from zep_python.memory import Memory
        from zep_python.user import User
    except ImportError:
        from zep import ZepClient
        from zep.document import Document
        from zep.document.collections import DocumentCollection
        from zep.memory import Memory
        from zep.user import User

class ZepQnASystem:
    def __init__(self, zep_api_url: str = "http://localhost:8000"):
        """
        Initialize Zep QnA system
        
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
        self.session_id = "qna_session"
        
    def load_entities_from_zep(self) -> List[Dict[str, Any]]:
        """
        Load entities from Zep collection
        
        Returns:
            List of entities from Zep
        """
        if not self.client:
            print("No Zep client available, using fallback")
            return self._load_from_json_fallback()
            
        try:
            # Get the collection
            collection = self.client.document.get_collection(self.collection_name)
            
            # Get all documents from the collection
            documents = collection.get_all()
            
            entities = []
            for doc in documents:
                # Extract entities from document metadata or content
                if hasattr(doc, 'metadata') and 'entities' in doc.metadata:
                    entities.extend(doc.metadata['entities'])
                else:
                    # Fallback: extract entities from document content
                    chunk_entities = self._extract_entities_from_text(doc.content)
                    entities.extend(chunk_entities)
            
            return entities
            
        except Exception as e:
            print(f"Error loading from Zep: {e}")
            print("Falling back to JSON file...")
            return self._load_from_json_fallback()
    
    def _load_from_json_fallback(self) -> List[Dict[str, Any]]:
        """
        Fallback to load entities from JSON file
        
        Returns:
            List of entities from JSON
        """
        json_files = ["zep_entities_results.json", "simple_entities_results.json"]
        
        for file_name in json_files:
            if os.path.exists(file_name):
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return data.get('entities', [])
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
        
        return []
    
    def _extract_entities_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text (fallback method)
        """
        entities = []
        
        # Extract person names
        person_pattern = r'\b(?:matt|kiera|ed|dave|sharris|jmalik|junaid malik)\b'
        persons = re.findall(person_pattern, text, re.IGNORECASE)
        
        # Extract system/technical entities
        system_pattern = r'\b(?:staging-3|corp-vpn3|corp-fs02|sw-07b|jenkins|buildconfig\.yaml|logi_loader\.dll)\b'
        systems = re.findall(system_pattern, text, re.IGNORECASE)
        
        # Extract time references
        time_pattern = r'\b(?:monday|tuesday|wednesday|3:11 am|6:12 am|7:41 am|2:47 am|4:23 am)\b'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        
        # Extract locations/areas
        location_pattern = r'\b(?:west wing|third floor|sales area|marketing workstations|training pc)\b'
        locations = re.findall(location_pattern, text, re.IGNORECASE)
        
        # Create entity objects
        for person in set(persons):
            entities.append({
                "type": "PERSON",
                "value": person.title(),
                "confidence": 0.9
            })
        
        for system in set(systems):
            entities.append({
                "type": "SYSTEM",
                "value": system,
                "confidence": 0.9
            })
        
        for time in set(times):
            entities.append({
                "type": "TIME",
                "value": time,
                "confidence": 0.9
            })
        
        for location in set(locations):
            entities.append({
                "type": "LOCATION",
                "value": location,
                "confidence": 0.8
            })
        
        return entities
    
    def search_entities(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for entities using Zep's search capabilities
        
        Args:
            query: Search query
            
        Returns:
            List of matching entities
        """
        if not self.client:
            return self._local_search_entities(query)
            
        try:
            # Use Zep's search functionality
            collection = self.client.document.get_collection(self.collection_name)
            search_results = collection.search(query, limit=10)
            
            entities = []
            for result in search_results:
                # Extract entities from search results
                if hasattr(result, 'metadata') and 'entities' in result.metadata:
                    entities.extend(result.metadata['entities'])
                else:
                    # Extract from content
                    chunk_entities = self._extract_entities_from_text(result.content)
                    entities.extend(chunk_entities)
            
            return entities
            
        except Exception as e:
            print(f"Zep search failed: {e}")
            # Fallback to local search
            return self._local_search_entities(query)
    
    def _local_search_entities(self, query: str) -> List[Dict[str, Any]]:
        """
        Local search for entities
        
        Args:
            query: Search query
            
        Returns:
            List of matching entities
        """
        entities = self.load_entities_from_zep()
        query_lower = query.lower()
        matches = []
        
        for entity in entities:
            # Search in entity value
            if query_lower in entity.get('value', '').lower():
                matches.append(entity)
            # Search in entity type
            elif query_lower in entity.get('type', '').lower():
                matches.append(entity)
        
        return matches
    
    def get_entity_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get entity by exact name
        
        Args:
            name: Entity name
            
        Returns:
            Entity dictionary or None
        """
        entities = self.load_entities_from_zep()
        
        for entity in entities:
            if entity.get('value', '').lower() == name.lower():
                return entity
        return None
    
    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all entities of a specific type
        
        Args:
            entity_type: Type of entities to find
            
        Returns:
            List of entities of the specified type
        """
        entities = self.load_entities_from_zep()
        return [e for e in entities if e.get('type', '').lower() == entity_type.lower()]
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using Zep's capabilities
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with answer and supporting information
        """
        question_lower = question.lower()
        
        # Question patterns and their handlers
        patterns = [
            (r'who is (\w+)', self._answer_who_is),
            (r'what (?:systems?|machines?) (?:did|does) (\w+) (?:access|use)', self._answer_what_systems),
            (r'when (?:did|was) (\w+) (?:happen|occur)', self._answer_when_event),
            (r'where (?:did|does) (\w+) (?:work|operate)', self._answer_where_work),
            (r'what (?:is|are) the (\w+)', self._answer_what_entities),
            (r'how many (\w+)', self._answer_how_many),
            (r'what (?:are|is) the (?:relationships?|connections?) (?:for|of) (\w+)', self._answer_relationships),
            (r'what (?:happened|occurred) at (\d+:\d+ \w+)', self._answer_timeline_event),
            (r'who (?:accessed|used) (\w+)', self._answer_who_accessed),
            (r'what (?:is|are) (\w+)', self._answer_what_is),
        ]
        
        for pattern, handler in patterns:
            match = re.search(pattern, question_lower)
            if match:
                return handler(match.groups(), question)
        
        # Default: search for entities
        return self._answer_general_search(question)
    
    def _answer_who_is(self, groups, question):
        """Answer 'who is X' questions"""
        entity_name = groups[0]
        entity = self.get_entity_by_name(entity_name)
        
        if entity:
            return {
                'question': question,
                'answer': f"{entity['value']} is a {entity['type']} entity",
                'entity': entity,
                'confidence': entity.get('confidence', 0.8),
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find information about {entity_name}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_what_systems(self, groups, question):
        """Answer 'what systems did X access' questions"""
        person_name = groups[0]
        systems = self.get_entities_by_type('SYSTEM')
        
        if systems:
            system_names = [sys['value'] for sys in systems]
            return {
                'question': question,
                'answer': f"{person_name.title()} could access: {', '.join(system_names)}",
                'systems': system_names,
                'confidence': 0.7,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find systems accessed by {person_name}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_when_event(self, groups, question):
        """Answer 'when did X happen' questions"""
        event_name = groups[0]
        time_entities = self.get_entities_by_type('TIME')
        
        if time_entities:
            times = [t['value'] for t in time_entities]
            return {
                'question': question,
                'answer': f"The event occurred at: {', '.join(times)}",
                'times': times,
                'confidence': 0.8,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find timing information for {event_name}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_where_work(self, groups, question):
        """Answer 'where did X work' questions"""
        person_name = groups[0]
        location_entities = self.get_entities_by_type('LOCATION')
        
        if location_entities:
            locations = [loc['value'] for loc in location_entities]
            return {
                'question': question,
                'answer': f"{person_name.title()} worked in: {', '.join(locations)}",
                'locations': locations,
                'confidence': 0.8,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find work locations for {person_name}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_what_entities(self, groups, question):
        """Answer 'what are the X' questions"""
        entity_type = groups[0]
        entities = self.get_entities_by_type(entity_type)
        
        if entities:
            values = [e['value'] for e in entities]
            return {
                'question': question,
                'answer': f"The {entity_type} entities are: {', '.join(values)}",
                'entities': entities,
                'count': len(entities),
                'confidence': 0.9,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find any {entity_type} entities",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_how_many(self, groups, question):
        """Answer 'how many X' questions"""
        entity_type = groups[0]
        entities = self.get_entities_by_type(entity_type)
        
        return {
            'question': question,
            'answer': f"There are {len(entities)} {entity_type} entities",
            'count': len(entities),
            'entities': entities,
            'confidence': 0.9,
            'source': 'zep_database' if self.client else 'fallback'
        }
    
    def _answer_relationships(self, groups, question):
        """Answer relationship questions"""
        entity_name = groups[0]
        entity = self.get_entity_by_name(entity_name)
        
        if entity:
            return {
                'question': question,
                'answer': f"Found relationships for {entity_name}: {entity['type']} entity with confidence {entity.get('confidence', 0.8)}",
                'entity': entity,
                'confidence': 0.8,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find relationships for {entity_name}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_timeline_event(self, groups, question):
        """Answer timeline event questions"""
        time_str = groups[0]
        time_entity = self.get_entity_by_name(time_str)
        
        if time_entity:
            return {
                'question': question,
                'answer': f"At {time_str}, events were recorded in the timeline",
                'entity': time_entity,
                'confidence': 0.8,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find information about {time_str}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_who_accessed(self, groups, question):
        """Answer 'who accessed X' questions"""
        system_name = groups[0]
        person_entities = self.get_entities_by_type('PERSON')
        
        if person_entities:
            people = [p['value'] for p in person_entities]
            return {
                'question': question,
                'answer': f"The following people could access {system_name}: {', '.join(people)}",
                'people': people,
                'confidence': 0.7,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find who accessed {system_name}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_what_is(self, groups, question):
        """Answer 'what is X' questions"""
        entity_name = groups[0]
        entity = self.get_entity_by_name(entity_name)
        
        if entity:
            entity_type = entity['type']
            confidence = entity.get('confidence', 0.8)
            
            return {
                'question': question,
                'answer': f"{entity_name} is a {entity_type} entity with confidence {confidence}",
                'entity': entity,
                'confidence': confidence,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': f"I couldn't find information about {entity_name}",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def _answer_general_search(self, question):
        """General search when no specific pattern matches"""
        # Search for entities mentioned in the question
        words = question.lower().split()
        matches = []
        
        for word in words:
            if len(word) > 3:  # Only search for words longer than 3 characters
                word_matches = self.search_entities(word)
                matches.extend(word_matches)
        
        # Remove duplicates
        unique_matches = []
        seen_values = set()
        for match in matches:
            if match['value'] not in seen_values:
                unique_matches.append(match)
                seen_values.add(match['value'])
        
        if unique_matches:
            entity_names = [m['value'] for m in unique_matches[:5]]  # Limit to 5
            return {
                'question': question,
                'answer': f"I found these relevant entities: {', '.join(entity_names)}",
                'entities': unique_matches,
                'confidence': 0.6,
                'source': 'zep_database' if self.client else 'fallback'
            }
        else:
            return {
                'question': question,
                'answer': "I couldn't find relevant information for your question. Try asking about specific people, systems, times, or locations mentioned in the story.",
                'confidence': 0.0,
                'source': 'zep_database' if self.client else 'fallback'
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded data
        
        Returns:
            Dictionary with statistics
        """
        entities = self.load_entities_from_zep()
        
        entity_types = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in entity_types:
                entity_types[entity_type] = 0
            entity_types[entity_type] += 1
        
        return {
            'total_entities': len(entities),
            'entity_types': entity_types,
            'source': 'zep_database' if self.client else 'fallback',
            'collection_name': self.collection_name if self.client else 'N/A'
        }

def interactive_zep_qna():
    """
    Interactive Zep QnA session
    """
    print("="*60)
    print("Zep QnA System for 'The Day Everything Slowed Down'")
    print("="*60)
    
    # Initialize Zep QnA system
    qna_system = ZepQnASystem()
    
    # Show statistics
    stats = qna_system.get_statistics()
    print(f"\nData Statistics:")
    print(f"- Total entities: {stats['total_entities']}")
    print(f"- Source: {stats['source']}")
    print(f"- Collection: {stats['collection_name']}")
    
    if 'entity_types' in stats:
        print(f"- Entity types: {', '.join(stats['entity_types'].keys())}")
    
    print(f"\nExample questions you can ask:")
    print("- Who is Matt?")
    print("- What systems did Matt access?")
    print("- When did the incident start?")
    print("- Where did Kiera work?")
    print("- What are the PERSON entities?")
    print("- How many SYSTEM entities are there?")
    print("- What are the relationships for staging-3?")
    print("- What happened at 3:11 am?")
    print("- Who accessed corp-vpn3?")
    print("- What is logi_loader.dll?")
    
    print(f"\nType 'quit' to exit, 'stats' for statistics, 'help' for examples")
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if question.lower() == 'quit':
                print("Goodbye!")
                break
            elif question.lower() == 'stats':
                stats = qna_system.get_statistics()
                print(f"\nStatistics:")
                for key, value in stats.items():
                    if isinstance(value, dict):
                        print(f"- {key}:")
                        for k, v in value.items():
                            print(f"  {k}: {v}")
                    else:
                        print(f"- {key}: {value}")
            elif question.lower() == 'help':
                print(f"\nExample questions:")
                print("- Who is Matt?")
                print("- What systems did Matt access?")
                print("- When did the incident start?")
                print("- Where did Kiera work?")
                print("- What are the PERSON entities?")
                print("- How many SYSTEM entities are there?")
                print("- What are the relationships for staging-3?")
                print("- What happened at 3:11 am?")
                print("- Who accessed corp-vpn3?")
                print("- What is logi_loader.dll?")
            elif question:
                answer = qna_system.answer_question(question)
                print(f"\nAnswer: {answer['answer']}")
                print(f"Confidence: {answer['confidence']:.2f}")
                print(f"Source: {answer.get('source', 'unknown')}")
                
                # Show additional details if available
                if 'entities' in answer and answer['entities']:
                    print(f"Found {len(answer['entities'])} relevant entities")
            else:
                print("Please enter a question.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """
    Main function
    """
    interactive_zep_qna()

if __name__ == "__main__":
    main() 