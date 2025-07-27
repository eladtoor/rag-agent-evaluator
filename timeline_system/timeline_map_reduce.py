from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from timeline_prompts import create_map_reduce_timeline_prompt, create_merge_timeline_prompt
from tqdm import tqdm

def map_reduce_timeline_function(file_path: str) -> str:
    """
    Create a timeline summary using Map-Reduce method.
    
    Args:
        file_path: Path to the text file to summarize
        
    Returns:
        A timeline summary with bullet points organized chronologically
    """
    # Load the document
    with open(file_path, 'r', encoding='utf-8') as file:
        
        text = file.read()
    
    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,      # ~2-3 events per chunk for better context
        chunk_overlap=150    # more overlap to preserve event transitions
    )
    chunks = splitter.split_text(text)
    
    # Initialize the language model
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Create timeline chains
    timeline_prompt_template = PromptTemplate(
        input_variables=["text"],
        template=create_map_reduce_timeline_prompt()
    )
    
    map_chain = timeline_prompt_template | llm | StrOutputParser()
    reduce_chain = PromptTemplate(
        input_variables=["text"],
        template=create_merge_timeline_prompt()
    ) | llm | StrOutputParser()
    
    # Apply map to each chunk
    print("📊 Processing chunks with Map-Reduce method...")
    chunk_timelines = []
    for chunk in tqdm(chunks, desc="🔄 Mapping chunks", unit="chunk"):
        timeline = map_chain.invoke({"text": chunk})
        chunk_timelines.append(timeline)
    
    # Combine all timelines
    print("🔄 Combining timelines...")
    combined_timelines = "\n\n".join(chunk_timelines)
    print("📊 Finalizing timeline with reduce step...")
    final_timeline = reduce_chain.invoke({"text": combined_timelines})
    
    return final_timeline 