"""
Indexing Chain - Data Preparation Pipeline

This pipeline happens BEFORE the RAG pipeline:

Document → Chunking → Embedding → Vector Database

This is the "setup" phase that prepares data for RAG queries.
"""

import os
import chromadb
import re
from openai import OpenAI
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import centralized path resolver
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.file_path_resolver import get_story_document_path, get_chroma_db_path

# Load environment variables
load_dotenv()

# Global variables - now using centralized path resolver
embedding_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path=get_chroma_db_path())
collection_name = "cybersecurity-story"

def step1_load_document(file_path: str) -> str:
    """
    STEP 1: Load the raw document
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Raw document text
    """
    print(f"🔗 INDEXING STEP 1: Loading document from '{file_path}'")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Loaded document: {len(content)} characters")
        return content
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return ""

def step2_chunking(document_text: str) -> list[dict]:
    """
    STEP 2: Split document into chunks
    
    This breaks the large document into smaller, manageable pieces
    that can be processed and retrieved effectively.
    
    Args:
        document_text: Raw document text
        
    Returns:
        List of chunk dictionaries with text and metadata
    """
    print(f"🔗 INDEXING STEP 2: Chunking document into smaller pieces")
    
    if not document_text:
        return []
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=250,      # Smaller chunks for more granular retrieval
        chunk_overlap=125,   # High overlap (50%) to preserve context between chunks
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    
    # Split the text into chunks
    text_chunks = text_splitter.split_text(document_text)
    
    # Create chunk objects with metadata
    chunks = []
    for i, chunk_text in enumerate(text_chunks):
        # Clean up the chunk text
        cleaned_chunk = chunk_text.strip()
        if not cleaned_chunk:
            continue
        
        # Extract time information if present (useful for cybersecurity timeline)
        time_pattern = r'\b(?:At\s+)?\d{1,2}:\d{2}\s*(?:AM|PM)\b'
        times_in_chunk = re.findall(time_pattern, cleaned_chunk)
        
        chunk_obj = {
            'id': f"chunk_{i}",
            'text': cleaned_chunk,
            'metadata': {
                'chunk_id': i,
                'length': len(cleaned_chunk),
                'has_time_marker': len(times_in_chunk) > 0,
                'times_found': ', '.join(times_in_chunk) if times_in_chunk else '',
                'document_title': 'The Day Everything Slowed Down',
                'source': 'cybersecurity_incident_story'
            }
        }
        chunks.append(chunk_obj)
    
    print(f"🧩 Created {len(chunks)} chunks")
    return chunks

def step3_embedding(chunks: list[dict]) -> list[dict]:
    """
    STEP 3: Create embeddings for each chunk
    
    Convert text chunks into vector representations that can be
    stored in a vector database for similarity search.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Chunks with embeddings added
    """
    print(f"🔗 INDEXING STEP 3: Creating embeddings for {len(chunks)} chunks")
    
    if not chunks:
        return []
    
    # Extract texts for batch embedding
    texts = [chunk['text'] for chunk in chunks]
    
    try:
        # Create embeddings in batch (more efficient)
        response = embedding_client.embeddings.create(
            model="text-embedding-3-large",
            input=texts
        )
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = response.data[i].embedding
        
        print(f"🎯 Created embeddings for {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        print(f"❌ Error creating embeddings: {e}")
        return []

def step4_vector_database_storage(chunks: list[dict]) -> bool:
    """
    STEP 4: Store chunks and embeddings in vector database
    
    Save the processed chunks to ChromaDB for later retrieval
    during the RAG pipeline.
    
    Args:
        chunks: List of chunks with embeddings
        
    Returns:
        Success status
    """
    print(f"🔗 INDEXING STEP 4: Storing {len(chunks)} chunks in vector database")
    
    if not chunks:
        return False
    
    try:
        # Try to get existing collection or create new one
        try:
            collection = chroma_client.get_collection(name=collection_name)
            print(f"📦 Using existing collection: {collection_name}")
        except:
            collection = chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Cybersecurity story chunks for RAG"}
            )
            print(f"📦 Created new collection: {collection_name}")
        
        # Prepare data for ChromaDB
        ids = [chunk['id'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        embeddings = [chunk['embedding'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Store in ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✅ Successfully stored {len(chunks)} chunks in vector database")
        return True
        
    except Exception as e:
        print(f"❌ Error storing in vector database: {e}")
        return False

def indexing_pipeline(file_path: str) -> bool:
    """
    Complete Indexing Pipeline - Prepares data for RAG
    
    This pipeline runs BEFORE the RAG pipeline:
    Document → Chunking → Embedding → Vector Database
    
    Args:
        file_path: Path to the document to index
        
    Returns:
        Success status
    """
    print(f"🔗 INDEXING PIPELINE STARTED")
    print(f"📄 Document: {file_path}")
    print("=" * 60)
    
    # Step 1: Load document
    document_text = step1_load_document(file_path)
    
    if not document_text:
        print("❌ Failed to load document")
        return False
    
    # Step 2: Chunking
    chunks = step2_chunking(document_text)
    
    if not chunks:
        print("❌ Failed to create chunks")
        return False
    
    # Step 3: Create embeddings
    chunks_with_embeddings = step3_embedding(chunks)
    
    if not chunks_with_embeddings:
        print("❌ Failed to create embeddings")
        return False
    
    # Step 4: Store in vector database
    success = step4_vector_database_storage(chunks_with_embeddings)
    
    if success:
        print(f"🔗 INDEXING PIPELINE COMPLETE")
        print("=" * 60)
        print("✅ Data is now ready for RAG queries!")
    else:
        print("❌ Indexing pipeline failed")
    
    return success

# Test the indexing pipeline
if __name__ == "__main__":
    print("🔗 Testing Indexing Pipeline")
    print("="*60)
    
    # Test with the cybersecurity story
    file_path = get_story_document_path()
    
    print(f"\n📄 Indexing document: {file_path}")
    success = indexing_pipeline(file_path)
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Document has been processed and stored")
        print("✅ Vector database is ready for RAG queries")
        print("\nNext step: Run RAG pipeline to answer questions!")
    else:
        print("\n❌ FAILED!")
        print("Check the error messages above")
    
    print("\n" + "="*60)
    print("Indexing Pipeline complete!") 