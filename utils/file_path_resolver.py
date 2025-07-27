import os
import sys
from pathlib import Path

def get_project_root():
    """
    Get the project root directory (mid-way_exercise).
    
    Returns:
        str: Absolute path to the project root directory
    """
    # Get the directory where this file is located (utils/)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get project root (mid-way_exercise)
    project_root = os.path.dirname(current_file_dir)
    return project_root

def get_story_document_path():
    """
    Get the absolute path to the main story document.
    
    This is the centralized way to get the story file path for both
    RAG indexing pipeline and Timeline generation.
    
    Returns:
        str: Absolute path to The_Day_Everything_Slowed_Down.txt
    """
    project_root = get_project_root()
    story_path = os.path.join(project_root, "The_Day_Everything_Slowed_Down.txt")
    return story_path

def get_chroma_db_path():
    """
    Get the absolute path to the ChromaDB directory.
    
    This ensures all components use the same vector database location.
    
    Returns:
        str: Absolute path to the chroma_db directory
    """
    project_root = get_project_root()
    chroma_path = os.path.join(project_root, "chroma_db")
    return chroma_path

def resolve_story_path(file_path):
    """
    Resolve the file path for a story, searching common folders if needed.
    
    DEPRECATED: Use get_story_document_path() instead for better consistency.
    This function is kept for backward compatibility with existing timeline tools.
    
    Args:
        file_path: The file path to resolve
        
    Returns:
        str: The resolved file path
        
    Raises:
        FileNotFoundError: If the file cannot be found in any location
    """
    print(f"⚠️  Using deprecated resolve_story_path(). Consider using get_story_document_path() instead.")
    
    # If it's the main story file, use the centralized path
    if file_path == "The_Day_Everything_Slowed_Down.txt":
        story_path = get_story_document_path()
        if os.path.isfile(story_path):
            print(f"✅ Found story document at: {story_path}")
            return story_path
        else:
            raise FileNotFoundError(f"Story document not found at: {story_path}")
    
    # For other files, use the old logic
    print(f"DEBUG: Looking for file: {file_path}")
    print(f"DEBUG: Current working directory: {os.getcwd()}")
    
    # Get the project root
    project_root = get_project_root()
    print(f"DEBUG: Project root: {project_root}")
    
    # Try as given (relative to current directory)
    if os.path.isfile(file_path):
        print(f"DEBUG: Found file at: {file_path}")
        return file_path
    
    # Try in project root (mid-way_exercise directory)
    root_path = os.path.join(project_root, file_path)
    print(f"DEBUG: Trying project root path: {root_path}")
    if os.path.isfile(root_path):
        print(f"DEBUG: Found file at: {root_path}")
        return root_path
    
    # Try just the filename in project root (in case user passed full path)
    filename = os.path.basename(file_path)
    if filename != file_path:  # Only if it's different
        root_filename_path = os.path.join(project_root, filename)
        print(f"DEBUG: Trying project root filename path: {root_filename_path}")
        if os.path.isfile(root_filename_path):
            print(f"DEBUG: Found file at: {root_filename_path}")
            return root_filename_path
    
    # Try in data/ (relative to project root)
    data_path = os.path.join(project_root, 'data', file_path)
    print(f"DEBUG: Trying data path: {data_path}")
    if os.path.isfile(data_path):
        print(f"DEBUG: Found file at: {data_path}")
        return data_path
    
    # Try in timeline_system/ (relative to project root)
    ts_path = os.path.join(project_root, 'timeline_system', file_path)
    print(f"DEBUG: Trying timeline_system path: {ts_path}")
    if os.path.isfile(ts_path):
        print(f"DEBUG: Found file at: {ts_path}")
        return ts_path
    
    # Try just the filename in data/ (in case user passed full path)
    if filename != file_path:  # Only if it's different
        data_filename_path = os.path.join(project_root, 'data', filename)
        print(f"DEBUG: Trying data filename path: {data_filename_path}")
        if os.path.isfile(data_filename_path):
            print(f"DEBUG: Found file at: {data_filename_path}")
            return data_filename_path
    
    # Not found
    print(f"DEBUG: File not found in any location")
    raise FileNotFoundError(f"Could not find file: {file_path}")

# Test the functions
if __name__ == "__main__":
    print("🔍 Testing File Path Resolver")
    print("="*50)
    
    print(f"📁 Project root: {get_project_root()}")
    print(f"📄 Story document: {get_story_document_path()}")
    print(f"🗄️  ChromaDB path: {get_chroma_db_path()}")
    
    # Test if story document exists
    story_path = get_story_document_path()
    if os.path.isfile(story_path):
        print(f"✅ Story document found!")
    else:
        print(f"❌ Story document not found at: {story_path}")
    
    print("\n✅ File Path Resolver test complete!") 