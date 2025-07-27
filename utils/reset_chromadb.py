import chromadb
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import file_path_resolver
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.file_path_resolver import get_chroma_db_path

load_dotenv()

def reset_chromadb():
    """Delete the existing ChromaDB collection to recreate with new embeddings"""
    
    # Initialize ChromaDB client with correct path
    chroma_client = chromadb.PersistentClient(path=get_chroma_db_path())
    collection_name = "cybersecurity-story"
    
    try:
        # Delete the existing collection
        chroma_client.delete_collection(name=collection_name)
        print(f"✅ Deleted existing collection: {collection_name}")
        
        # Verify it's gone
        try:
            collection = chroma_client.get_collection(name=collection_name)
            print("❌ Collection still exists!")
        except:
            print("✅ Collection successfully deleted")
            
    except Exception as e:
        print(f"❌ Error deleting collection: {e}")

if __name__ == "__main__":
    reset_chromadb() 