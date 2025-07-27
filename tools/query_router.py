"""
Query Router for Timeline vs RAG Classification

This file contains a simple AI-powered router that classifies user questions
and decides whether to use timeline tools or RAG tools.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_question(question: str) -> str:
    """
    Classify a user question as either 'timeline' or 'rag_qa'.
    
    Args:
        question: The user's question
        
    Returns:
        'timeline' or 'rag_qa'
    """
    try:
        # Create classification prompt
        prompt = f"""You are a helpful assistant that classifies questions.

Classify the following question as either 'timeline' or 'rag_qa':

Question: {question}

Rules:
- Use 'timeline' for: creating timelines, summarizing events, chronological summaries
- Use 'rag_qa' for: specific questions about times, people, files, details

Examples:
- "Create a timeline" → timeline
- "Summarize the events" → timeline
- "What time did X happen?" → rag_qa
- "Who was involved?" → rag_qa
- "What was the file name?" → rag_qa

Answer with only 'timeline' or 'rag_qa':"""

        # Get classification from OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a classification assistant. Respond with only 'timeline' or 'rag_qa'."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        
        # Clean the response
        classification = response.choices[0].message.content.strip().lower()
        
        # Validate response
        if classification in ['timeline', 'rag_qa']:
            return classification
        else:
            # Default to rag_qa if unclear
            return 'rag_qa'
            
    except Exception as e:
        print(f"Error classifying question: {e}")
        # Default to rag_qa if there's an error
        return 'rag_qa'

def get_router_tools():
    """Get router tools for use with agents"""
    return [classify_question]

# Test the router
if __name__ == "__main__":
    print("🔍 Testing Query Router...")
    
    # Test questions
    test_questions = [
        "Create a timeline of the cybersecurity incident",
        "What time did the attack start?",
        "Summarize the events in chronological order",
        "Who was the main suspect?",
        "What was the name of the suspicious file?"
    ]
    
    for question in test_questions:
        classification = classify_question(question)
        print(f"\nQuestion: {question}")
        print(f"Classification: {classification}")
    
    print("\n✅ Query Router test complete!") 