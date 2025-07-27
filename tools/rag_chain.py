"""
RAG Chain - Beginner-Friendly Pipeline for Q&A System

This file creates a simple RAG pipeline:

R = Retrieval   (Step 1: Get relevant documents)
A = Augmentation (Step 2: Format docs to augment the prompt)  
G = Generation  (Step 3: LLM generates answer with augmented context)

Question → Retrieval → Augmentation → Generation → Answer

No complex classes - just simple functions!
"""

import os
import chromadb
import re
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool

# Import centralized path resolver
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.file_path_resolver import get_chroma_db_path

# Simple RAG without reranking

# Load environment variables
load_dotenv()

# Global variables - now using centralized path resolver
chroma_client = chromadb.PersistentClient(path=get_chroma_db_path())
collection_name = "cybersecurity-story"
embedding_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.3)

# Try to connect to ChromaDB
try:
    collection = chroma_client.get_collection(name=collection_name)
    print(f"✅ Connected to ChromaDB: {collection_name}")
except:
    print(f"❌ Collection {collection_name} not found!")
    collection = None

def step1_retrieval(question: str, top_k: int = 3, use_reranking: bool = True, rerank_method: str = "hybrid") -> list[str]:
    """
    R = RETRIEVAL: Get relevant documents from ChromaDB with optional reranking
    
    This step searches the vector database for chunks that are semantically
    similar to the user's question, then optionally reranks them for better precision.
    
    Args:
        question: User's question
        top_k: Number of chunks to retrieve finally
        use_reranking: Whether to apply reranking for better precision
        rerank_method: Reranking method ("hybrid", "semantic", "keyword", "llm", "none")
        
    Returns:
        List of relevant text chunks (reranked if enabled)
    """
    print(f"🔗 STEP 1 - RETRIEVAL: Getting documents for '{question}'")
    
    if not collection:
        print("❌ No database connection")
        return []
    
    # Retrieve more chunks initially if reranking is enabled
    initial_k = top_k
    
    # Get embedding for the question
    question_embedding = embedding_client.embeddings.create(
        model="text-embedding-3-large",
        input=question
    ).data[0].embedding
    
    # Search ChromaDB for similar chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=initial_k
    )
    
    chunks = results['documents'][0] if results['documents'][0] else []
    
    # Take top_k chunks (no reranking)
    chunks = chunks[:top_k]
    
    # Print retrieved chunks with better organization
    print("\n" + "="*60)
    print("🔍 CHUNKS RETRIEVED FROM VECTOR DATABASE")
    print("="*60)
    print(f"📊 Total chunks retrieved: {len(chunks)}")
    print("-"*60)
    
    for i, chunk in enumerate(chunks, 1):
        # Truncate long chunks for readability
        chunk_preview = chunk[:200] + "..." if len(chunk) > 200 else chunk
        print(f"📄 Chunk {i}:")
        print(f"   {chunk_preview}")
        print()
    
    print("="*60)
    
    return chunks

def step2_augmentation(chunks: list[str], question: str) -> str:
    """
    A = AUGMENTATION: Format retrieved docs to augment the LLM prompt
    
    This is the "A" in RAG! We take the retrieved documents and 
    format them into a context that augments/enhances the LLM prompt.
    
    Args:
        chunks: List of relevant text chunks from retrieval
        question: Original user question
        
    Returns:
        Augmented prompt with context
    """
    print(f"🔗 STEP 2 - AUGMENTATION: Formatting context to augment prompt")
    
    if not chunks:
        context = "No relevant information found."
    else:
        # Combine retrieved chunks into context
        context = "\n\n".join(chunks)
    
    # Create augmented prompt (context + question)
    augmented_prompt = f"""You are a cybersecurity expert analyzing a cybersecurity incident.
Answer the following question based on the provided context.
Be accurate, concise, and provide specific details when available.

CONTEXT (Retrieved Documents):
{context}

QUESTION: {question}

ANSWER:"""
    
    print(f"📄 Augmented prompt with {len(chunks)} documents")
    print(f"📝 Total context length: {len(context)} characters")
    print(f"🔗 Context will be used to generate answer")
    return augmented_prompt

def step3_generation(augmented_prompt: str) -> str:
    """
    G = GENERATION: LLM generates answer using the augmented prompt
    
    Args:
        augmented_prompt: Prompt enhanced with retrieved context
        
    Returns:
        Generated answer
    """
    print(f"🔗 STEP 3 - GENERATION: LLM generating answer")
    
    # Get answer from LLM using the augmented prompt
    response = llm.invoke(augmented_prompt)
    return response.content

def rag_pipeline(question: str) -> str:
    """
    Complete RAG Pipeline - Simple and Clear!
    
    R-A-G Structure:
    R = Retrieval   → Get relevant documents from database
    A = Augmentation → Format docs to augment/enhance the prompt  
    G = Generation  → LLM generates answer with enhanced prompt
    
    Args:
        question: User's question
        
    Returns:
        Generated answer
    """
    # RAG Pipeline execution
    
    # R = RETRIEVAL: Get relevant documents
    chunks = step1_retrieval(question)
    
    if not chunks:
        return "No relevant information found in the documents."
    
    # A = AUGMENTATION: Format docs to augment the prompt
    augmented_prompt = step2_augmentation(chunks, question)
    
    # G = GENERATION: LLM generates answer with augmented context
    answer = step3_generation(augmented_prompt)
    
    # Pipeline complete
    
    return answer

# Modern LCEL version (still simple!)
def create_simple_lcel_chain():
    """
    Create a simple LCEL chain - the modern way!
    
    LCEL = LangChain Expression Language
    Uses the | operator to chain R-A-G steps together
    """
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser
    
    print("🔗 Creating LCEL Chain (Modern LangChain)")
    
    # Simple function that does R (Retrieval) and A (Augmentation)
    def retrieval_and_augmentation(question):
        # R = Retrieval
        chunks = step1_retrieval(question)
        # A = Augmentation (but we need to return just context for LCEL)
        if not chunks:
            return "No relevant information found."
        else:
            return "\n\n".join(chunks)
    
    # Create simple prompt template for LCEL
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a cybersecurity expert analyzing a cybersecurity incident.

CONTEXT: {context}
QUESTION: {question}
ANSWER:"""
    )
    
    # The LCEL chain: input → retrieval+augmentation → prompt → llm → parse
    # This represents: R-A-G in the | pipeline
    chain = (
        {"context": retrieval_and_augmentation, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# Tool wrapper for the agent
@tool
def rag_chain_search_and_answer(question: str) -> str:
    """
    Simple RAG chain tool for the agent.
    
    This shows the complete pipeline in action:
    Question → Retrieval → Reranking → Generation → Answer
    
    Args:
        question: The question to answer
        
    Returns:
        Generated answer from the RAG pipeline
    """
    try:
        print(f"🔗 Using Simple RAG Pipeline")
        answer = rag_pipeline(question)
        return answer
    except Exception as e:
        return f"Error in RAG pipeline: {str(e)}"

def get_rag_chain_tools():
    """Get RAG chain tools for use with agents"""
    return [rag_chain_search_and_answer]

# Test the pipeline
if __name__ == "__main__":
    print("🔗 Testing Simple RAG Pipeline")
    print("="*60)
    
    # Test questions
    test_questions = [
        "What time did the attack start?",
        "Who was the main suspect?",
        "What was the name of the suspicious file?",
    ]
    
    print("\n1️⃣ Testing Simple RAG Pipeline:")
    print("-" * 40)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        answer = rag_pipeline(question)
        print(f"💡 Answer: {answer}")
        print()
    
    print("\n2️⃣ Testing LCEL Chain:")
    print("-" * 40)
    
    try:
        lcel_chain = create_simple_lcel_chain()
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            answer = lcel_chain.invoke(question)
            print(f"💡 Answer: {answer}")
            print()
            
    except Exception as e:
        print(f"❌ LCEL Error: {e}")
    
    print("✅ Simple RAG Pipeline testing complete!") 