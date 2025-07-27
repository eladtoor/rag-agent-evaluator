from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path so we can import from it
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from tools.timeline_tools import get_timeline_tools
from tools.rag_chain import get_rag_chain_tools  # Use proper RAG chain tools
from tools.query_router import classify_question
from utils.file_path_resolver import get_chroma_db_path

# Load environment variables from project root
load_dotenv(dotenv_path=project_root.parent / ".env")

def create_story_analysis_agent():
    """Create a story analysis agent that can do timeline summarization and RAG Q&A"""
    
    # Get all tools
    timeline_tools = get_timeline_tools()
    qa_tools = get_rag_chain_tools() # Use the proper RAG chain tools
    all_tools = timeline_tools + qa_tools
    
    # Create the language model
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a story analysis agent specialized in answering questions about cybersecurity incidents.

Your primary function is to answer specific questions about "The Day Everything Slowed Down" story using a complete RAG Chain Pipeline.

Available Tools:
- rag_chain_search_and_answer: Complete RAG pipeline (Question → Retrieval → Augmentation → Generation → Answer)
- map_reduce_timeline: Create timeline summary using Map-Reduce method
- refine_timeline: Create timeline summary using Refine method

The RAG Chain Pipeline (R-A-G):
1.  R = Retrieval: Get relevant documents from vector database
2.  A = Augmentation: Format docs to augment/enhance the prompt  
3.  G = Generation: LLM generates answer with enhanced context
4.  Pipeline Complete: Returns the final answer

Timeline Tools:
- map_reduce_timeline: Processes document in chunks and combines results
- refine_timeline: Iteratively improves timeline with each chunk

This demonstrates the complete "chain" structure with clear R-A-G steps:
Input → R → A → G → Output

Available documents:
- "The Day Everything Slowed Down.txt"

Be precise and factual in your responses. The RAG chain will handle the complete pipeline automatically."""),
        ("human", "Request type: {request_type}\nUser question: {input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, all_tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=all_tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=30  # Allow more iterations to complete both timelines
    )
    
    return agent_executor

def handle_timeline_request(agent, user_input):
    """Use the agent to execute timeline tools properly"""
    print("="*50)
    print("📋 TIMELINE GENERATION STARTED")
    print("="*50)
    
    # Use the agent to execute timeline tools
    timeline_prompt = f"""
    Please generate both timeline summaries for the cybersecurity incident story.
    
    User request: {user_input}
    
    Please use both timeline tools:
    1. First use the map_reduce_timeline tool to create a Map-Reduce timeline
    2. Then use the refine_timeline tool to create a Refine timeline
    
    File path: The_Day_Everything_Slowed_Down.txt
    """
    
    try:
        response = agent.invoke({
            "input": timeline_prompt,
            "request_type": "TIMELINE"
        })
        print("✅ Timeline generation completed through agent!")
        print(f"\nAgent Response: {response['output']}")
    except Exception as e:
        print(f"❌ Error in timeline generation: {e}")
        return
    
    print("="*50)
    print("🎉 TIMELINES GENERATED SUCCESSFULLY!")
    print("="*50)

def main():
    """Main function to run the story analysis agent"""
    
    # Ensure we're in the correct working directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 Working directory set to: {os.getcwd()}")
    
    print("="*60)
    print("STORY ANALYSIS AGENT")
    print("="*60)
    
    # Check if vector database is set up for RAG questions
    print("\n🔍 Checking system readiness...")
    
    import chromadb
    try:
        # Use absolute path based on project root
        project_root = Path(__file__).parent.parent  # mid-way_exercise
        chroma_db_path = get_chroma_db_path()
        chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))
        collection = chroma_client.get_collection(name="cybersecurity-story")
        print("✅ Vector database is ready for RAG questions")
    except:
        print("⚠️  Vector database not found!")
        print("\n📋 SETUP REQUIRED:")
        print("Before using RAG Q&A, you need to run the indexing pipeline:")
        print("1. cd tools")
        print("2. python indexing_chain.py")
        print("\nThis will process the document and create the vector database.")
        print("Timeline requests will work without this setup.")
        print("\n" + "="*60)
    
    print("\nThis agent can handle two types of requests:")
    print("\n📋 TIMELINE REQUESTS:")
    print("1. Create timeline summaries using Map-Reduce method")
    print("2. Create timeline summaries using Refine method")
    print("3. Save both results to separate files")
    
    print("\n🔍 RAG Q&A REQUESTS:")
    print("1. Answer specific questions about the cybersecurity incident")
    print("2. Find relevant information from the document")
    print("3. Generate detailed answers using AI")
    print("   (Requires vector database setup - see above)")
    
    print("\n📁 Available documents:")
    print("- The Day Everything Slowed Down (automatically used)")
    
    print("\nExample usage:")
    print("- 'Create a timeline' or 'summarize the story'")
    print("- 'What time did the attack start?'")
    print("- 'Who was the main suspect?'")
    print("- 'What was the name of the suspicious file?'")
    
    print("\nType 'quit' to exit")
    print("-"*60)
    
    # Create the agent
    agent = create_story_analysis_agent()
    
    # Start conversation
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        try:
            # Classify the question first
            classification = classify_question(user_input)
            print(f"\n🔍 Question type: {classification.upper()}")
            
            # Handle timeline requests with forced dual execution
            if classification.upper() == "TIMELINE":
                handle_timeline_request(agent, user_input)
            else:
                # Pass the classification to the agent for RAG Q&A
                response = agent.invoke({
                    "input": user_input,
                    "request_type": classification.upper()
                })
                print(f"\nAssistant: {response['output']}")
            
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again with a different request.")
            print("If you're asking a Q&A question, try rephrasing it more clearly.")

if __name__ == "__main__":
    main() 