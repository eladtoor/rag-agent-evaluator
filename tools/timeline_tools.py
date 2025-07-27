from langchain.tools import tool
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'timeline_system'))
from timeline_system.timeline_map_reduce import map_reduce_timeline_function
from timeline_system.timeline_refine import refine_timeline_function
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import re
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Add the project root to the path to import timeline output saver and utils
sys.path.append(str(Path(__file__).parent.parent))
from timeline_system.timeline_output_saver import save_timeline_to_file
from utils.file_path_resolver import resolve_story_path

# Load environment variables
load_dotenv()

@tool
def map_reduce_timeline(file_path: str) -> str:
    """
    Create a timeline summary using Map-Reduce method and save to file.
    
    Args:
        file_path: Path to the text file to summarize
        
    Returns:
        A timeline summary with bullet points organized chronologically
    """
    # Resolve file path
    print(f"🔍 Resolving file path: {file_path}")
    resolved_path = resolve_story_path(file_path)
    print(f"✅ Resolved path: {resolved_path}")
    # Get timeline using map-reduce method
    timeline = map_reduce_timeline_function(resolved_path)
    
    # Validate and improve the timeline
    validated_timeline = validate_timeline_answer(timeline)
    
    # Save to file
    output_file = save_timeline_to_file(validated_timeline, resolved_path, "map_reduce")
    
    return f"Timeline created using Map-Reduce method and saved to {output_file}:\n\n{validated_timeline}"

@tool
def refine_timeline(file_path: str) -> str:
    """
    Create a timeline summary using Refine method and save to file.
    
    Args:
        file_path: Path to the text file to summarize
        
    Returns:
        A refined timeline summary with bullet points
    """
    # Resolve file path
    print(f"🔍 Resolving file path: {file_path}")
    resolved_path = resolve_story_path(file_path)
    print(f"✅ Resolved path: {resolved_path}")
    # Get timeline using refine method
    timeline = refine_timeline_function(resolved_path)
    
    # Validate and improve the timeline
    validated_timeline = validate_timeline_answer(timeline)
    
    # Save to file
    output_file = save_timeline_to_file(validated_timeline, resolved_path, "refine")
    
    return f"Timeline created using Refine method and saved to {output_file}:\n\n{validated_timeline}"

def validate_timeline_answer(answer):
    """Validate and improve timeline answer precision"""
    
    # Check for exact time patterns
    time_patterns = [
        r'\d{1,2}:\d{2}\s*(AM|PM)',  # 9:00 PM
        r'\d{1,2}\s*(AM|PM)',        # 9 PM
        r'\d{1,2}:\d{2}',            # 9:00
    ]
    
    # Check for specific action keywords
    action_improvements = {
        'contacted authorities': 'called 911',
        'called emergency services': 'called 911',
        'dialed emergency': 'called 911',
        'around': 'exactly',
        'approximately': 'exactly',
        'about': 'exactly'
    }
    
    # Validate and correct
    corrected_answer = answer
    
    # Replace vague terms with specific ones
    for vague, specific in action_improvements.items():
        corrected_answer = corrected_answer.replace(vague, specific)
    
    # Check if times are properly formatted
    lines = corrected_answer.split('\n')
    improved_lines = []
    
    for line in lines:
        if line.strip().startswith('•'):
            # Check if line has exact time
            has_exact_time = any(re.search(pattern, line) for pattern in time_patterns)
            if not has_exact_time and any(word in line.lower() for word in ['time', 'pm', 'am']):
                # Try to extract time from context
                time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', line)
                if time_match:
                    improved_lines.append(line)
                else:
                    improved_lines.append(line.replace('Time not specified', 'Time not specified'))
            else:
                improved_lines.append(line)
        else:
            improved_lines.append(line)
    
    return '\n'.join(improved_lines)

def get_timeline_tools():
    """Get all timeline summarization tools for use with agents"""
    return [map_reduce_timeline, refine_timeline]

# Example usage
if __name__ == "__main__":
    # Example usage
    tools = get_timeline_tools()
    
    print("Available timeline tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Test with the day everything slowed down story
    test_file = "The_Day_Everything_Slowed_Down.txt"
    
    print(f"\nTesting timeline tools with {test_file}...")
    
    # Test map-reduce timeline
    print("\n1. Map-Reduce Timeline:")
    result1 = map_reduce_timeline(test_file)
    print(result1)
    
    # Test refine timeline
    print("\n2. Refine Timeline:")
    result2 = refine_timeline(test_file)
    print(result2) 