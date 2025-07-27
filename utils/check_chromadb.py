import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

def check_chromadb_collection():
    """Check the ChromaDB collection and count chunks"""
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "cybersecurity-story"
    
    try:
        # Get the collection
        collection = chroma_client.get_collection(name=collection_name)
        
        # Get all documents to count them
        results = collection.get()
        
        num_chunks = len(results['ids'])
        print(f"✅ ChromaDB Collection: {collection_name}")
        print(f"📊 Total chunks stored: {num_chunks}")
        
        # Show some sample chunk IDs
        if num_chunks > 0:
            print(f"\n📝 Sample chunk IDs:")
            for i, chunk_id in enumerate(results['ids'][:5]):
                print(f"  {i+1}. {chunk_id}")
            
            if num_chunks > 5:
                print(f"  ... and {num_chunks - 5} more chunks")
        
        # Show chunk sizes
        if num_chunks > 0:
            print(f"\n📏 Chunk size analysis:")
            chunk_lengths = [len(doc) for doc in results['documents']]
            avg_length = sum(chunk_lengths) / len(chunk_lengths)
            min_length = min(chunk_lengths)
            max_length = max(chunk_lengths)
            
            print(f"  Average chunk length: {avg_length:.0f} characters")
            print(f"  Shortest chunk: {min_length} characters")
            print(f"  Longest chunk: {max_length} characters")
        
        return num_chunks
        
    except Exception as e:
        print(f"❌ Error accessing ChromaDB collection: {e}")
        return 0

if __name__ == "__main__":
    check_chromadb_collection() 