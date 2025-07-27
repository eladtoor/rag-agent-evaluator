import os
import sys
from datetime import datetime
from pathlib import Path

# Import centralized path resolver
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.file_path_resolver import get_project_root

def save_timeline_to_file(timeline_content: str, file_path: str, method: str) -> str:
    """
    Save timeline content to a file with timestamp to avoid overwriting.
    
    This function creates timestamped output files in the agents/outputs/ directory
    to preserve all timeline generations without overwriting previous results.
    
    Args:
        timeline_content: The timeline text to save
        file_path: Original source file path (used for naming)
        method: The method used ("map_reduce" or "refine")
        
    Returns:
        str: The absolute path to the saved output file
    """
    # Use centralized path resolver to get project root
    project_root = get_project_root()
    
    # Always save to agents/outputs directory (centralized location)
    outputs_dir = os.path.join(project_root, "agents", "outputs")
    
    # Create outputs directory if it doesn't exist
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
        print(f"📁 Created outputs directory: {outputs_dir}")
    
    # Extract just the filename without path and extension
    filename = os.path.basename(file_path)
    base_name = filename.replace('.txt', '')
    
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{method}_timeline_{base_name}_{timestamp}.txt"
    output_file = os.path.join(outputs_dir, output_filename)
    
    # Save to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(timeline_content)
        
        print(f"✅ Timeline saved: {output_filename}")
        return output_file
        
    except Exception as e:
        print(f"❌ Error saving timeline: {e}")
        raise

def get_latest_timeline_file(method: str, story_name: str = None) -> str:
    """
    Get the path to the most recently created timeline file.
    
    Args:
        method: Timeline method ("map_reduce" or "refine")
        story_name: Optional story name filter (default: any story)
        
    Returns:
        str: Path to the latest timeline file, or None if not found
    """
    project_root = get_project_root()
    outputs_dir = os.path.join(project_root, "agents", "outputs")
    
    if not os.path.exists(outputs_dir):
        return None
    
    # Find matching files
    pattern_start = f"{method}_timeline_"
    if story_name:
        pattern_start += story_name.replace('.txt', '')
    
    matching_files = []
    for file in os.listdir(outputs_dir):
        if file.startswith(pattern_start) and file.endswith('.txt'):
            file_path = os.path.join(outputs_dir, file)
            matching_files.append((file_path, os.path.getctime(file_path)))
    
    if not matching_files:
        return None
    
    # Return the most recent file
    latest_file = max(matching_files, key=lambda x: x[1])
    return latest_file[0]

def list_timeline_outputs() -> list:
    """
    List all timeline output files with their creation times.
    
    Returns:
        list: List of tuples (filename, creation_time, method)
    """
    project_root = get_project_root()
    outputs_dir = os.path.join(project_root, "agents", "outputs")
    
    if not os.path.exists(outputs_dir):
        return []
    
    timeline_files = []
    for file in os.listdir(outputs_dir):
        if file.endswith('.txt') and ('_timeline_' in file):
            file_path = os.path.join(outputs_dir, file)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            # Extract method from filename
            method = "unknown"
            if file.startswith("map_reduce_timeline_"):
                method = "map_reduce"
            elif file.startswith("refine_timeline_"):
                method = "refine"
            
            timeline_files.append((file, creation_time, method))
    
    # Sort by creation time (newest first)
    timeline_files.sort(key=lambda x: x[1], reverse=True)
    return timeline_files

# Test the functions
if __name__ == "__main__":
    print("🔍 Testing Timeline Output Saver")
    print("="*50)
    
    project_root = get_project_root()
    print(f"📁 Project root: {project_root}")
    
    outputs_dir = os.path.join(project_root, "agents", "outputs")
    print(f"📁 Outputs directory: {outputs_dir}")
    
    # List existing timeline files
    timeline_files = list_timeline_outputs()
    if timeline_files:
        print(f"\n📄 Found {len(timeline_files)} timeline files:")
        for filename, creation_time, method in timeline_files[:5]:  # Show first 5
            print(f"  ✅ {filename} ({method}) - {creation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if len(timeline_files) > 5:
            print(f"  ... and {len(timeline_files) - 5} more files")
    else:
        print("📄 No timeline files found")
    
    print("\n✅ Timeline Output Saver test complete!") 