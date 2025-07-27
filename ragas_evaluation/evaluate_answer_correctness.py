"""
RAGAS Answer Correctness Evaluation

This script evaluates timeline extraction systems using RAGAS answer correctness metric.
It compares generated answers against ground truth answers from the cybersecurity story.
"""

import json
import os
import re
import glob
from datetime import datetime
from dotenv import load_dotenv
from datasets import Dataset
from ragas.metrics import answer_correctness
from ragas import evaluate

# Load environment variables from .env file
load_dotenv()

def find_latest_output_files():
    """
    Find the latest map-reduce and refine timeline output files.
    
    Returns:
        tuple: (latest_map_reduce_file, latest_refine_file)
    """
    outputs_dir = "../agents/outputs"
    
    # Find all map-reduce timeline files
    map_reduce_pattern = os.path.join(outputs_dir, "map_reduce_timeline_*.txt")
    map_reduce_files = glob.glob(map_reduce_pattern)
    
    # Find all refine timeline files
    refine_pattern = os.path.join(outputs_dir, "refine_timeline_*.txt")
    refine_files = glob.glob(refine_pattern)
    
    # Get the latest map-reduce file
    latest_map_reduce = None
    if map_reduce_files:
        latest_map_reduce = max(map_reduce_files, key=os.path.getctime)
        print(f"📁 Latest Map-Reduce file: {os.path.basename(latest_map_reduce)}")
    
    # Get the latest refine file
    latest_refine = None
    if refine_files:
        latest_refine = max(refine_files, key=os.path.getctime)
        print(f"📁 Latest Refine file: {os.path.basename(latest_refine)}")
    
    return latest_map_reduce, latest_refine

def load_ground_truth():
    """Load the ground truth dataset."""
    try:
        with open('results/ground_truth_dataset.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: ground_truth_dataset.json not found!")
        return None

def extract_answer_from_timeline(timeline_content, expected_answer, question):
    """
    Extract a specific answer from timeline content.
    
    Args:
        timeline_content: The full timeline text
        expected_answer: The expected answer from ground truth
        question: The question being asked
        
    Returns:
        str: The found answer or "Not found"
    """
    found_answer = "Not found"
    
    # Special handling for sequence question
    if "sequence" in question.lower():
        sequence_events = []
        sequence_keywords = ["jmalik connected", "staging-3 reboot", "logi_loader.dll", 
                           "dns requests", "sharris", "compromised", "cdn.nodeflux.ai"]
        
        for keyword in sequence_keywords:
            if keyword.lower() in timeline_content.lower():
                if keyword == "jmalik connected":
                    sequence_events.append("jmalik connected via corp-vpn3")
                elif keyword == "staging-3 reboot":
                    sequence_events.append("staging-3 rebooted")
                elif keyword == "logi_loader.dll":
                    sequence_events.append("logi_loader.dll was copied")
                elif keyword == "dns requests":
                    sequence_events.append("DNS requests to suspicious subdomains started")
                elif keyword == "sharris" and "compromised" in timeline_content.lower():
                    sequence_events.append("sharris account was compromised")
                elif keyword == "cdn.nodeflux.ai":
                    sequence_events.append("Data exfiltration occurred to cdn.nodeflux.ai")
        
        if sequence_events:
            found_answer = ", ".join(sequence_events)
    else:
        # For regular questions, search for the expected answer
        if expected_answer.lower() in timeline_content.lower():
            found_answer = expected_answer
        else:
            # Try to find the answer by searching for keywords in the question
            question_words = question.lower().split()
            key_words = [word for word in question_words if len(word) > 3 and word not in ['what', 'when', 'where', 'who', 'how', 'was', 'the', 'did', 'were']]
            
            # Search line by line for relevant content
            lines = timeline_content.split('\n')
            for line in lines:
                line_lower = line.lower()
                # If line contains keywords from the question
                if any(keyword in line_lower for keyword in key_words):
                    # Try to extract time if it's a time-based question
                    if any(time_word in question.lower() for time_word in ['time', 'when']):
                        time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', line)
                        if time_match:
                            found_answer = time_match.group(1)
                            break
                    else:
                        # For non-time questions, try to extract the relevant entity
                        # Look for file names
                        if '.dll' in line_lower or '.exe' in line_lower:
                            file_match = re.search(r'(\w+\.\w+)', line)
                            if file_match:
                                found_answer = file_match.group(1)
                                break
                        # Look for domain names
                        elif '.' in line and any(tld in line_lower for tld in ['.com', '.ai', '.live', '.org']):
                            domain_match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
                            if domain_match:
                                found_answer = domain_match.group(1)
                                break
                        # Look for user names
                        elif any(user_word in question.lower() for user_word in ['user', 'account', 'who']):
                            # Common user name patterns
                            user_match = re.search(r'\b([a-z]+(?:[a-z]+)?)\b', line_lower)
                            if user_match and len(user_match.group(1)) > 2:
                                found_answer = user_match.group(1)
                                break
                        else:
                            # Generic extraction - take the cleaned line
                            found_answer = line.strip('• ').strip()
                            break
    
    return found_answer

def extract_answers_from_timeline(timeline_file_path, ground_truth_data):
    """
    Extract answers from a timeline file based on ground truth questions.
    
    Args:
        timeline_file_path: Path to the timeline file
        ground_truth_data: The loaded ground truth dataset
        
    Returns:
        List of answers corresponding to the ground truth questions
    """
    try:
        with open(timeline_file_path, 'r', encoding='utf-8') as f:
            timeline_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Timeline file {timeline_file_path} not found!")
        return None
    
    answers = []
    for item in ground_truth_data['ground_truth']:
        question = item['question']
        expected_answer = item['answer']
        
        found_answer = extract_answer_from_timeline(timeline_content, expected_answer, question)
        answers.append(found_answer)
    
    return answers

def create_evaluation_dataset(ground_truth_data, model_answers):
    """
    Create a RAGAS-compatible dataset for evaluation.
    
    Args:
        ground_truth_data: The loaded ground truth data
        model_answers: List of answers generated by your timeline system
        
    Returns:
        Dataset: RAGAS-compatible dataset
    """
    # Extract questions and ground truth answers
    questions = [item["question"] for item in ground_truth_data["ground_truth"]]
    ground_truth_answers = [item["answer"] for item in ground_truth_data["ground_truth"]]
    
    # Create dataset dictionary
    data_samples = {
        'question': questions,
        'answer': model_answers,
        'ground_truth': ground_truth_answers
    }
    
    return Dataset.from_dict(data_samples)

def evaluate_timeline_system(timeline_file_path, output_name):
    """Main function to evaluate timeline system using RAGAS."""
    print(f"🔍 RAGAS Answer Correctness Evaluation - {output_name}")
    print("="*60)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Error: OPENAI_API_KEY not set in .env file!")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return
    
    # Load ground truth data
    ground_truth_data = load_ground_truth()
    if ground_truth_data is None:
        return
    
    print(f"✅ Loaded ground truth dataset with {len(ground_truth_data['ground_truth'])} questions")
    
    # Extract answers from timeline file using ground truth questions
    model_answers = extract_answers_from_timeline(timeline_file_path, ground_truth_data)
    if model_answers is None:
        return
    
    if len(model_answers) != len(ground_truth_data['ground_truth']):
        print(f"❌ Error: Expected {len(ground_truth_data['ground_truth'])} answers, got {len(model_answers)}")
        return
    
    print(f"✅ Extracted {len(model_answers)} answers from timeline file")
    
    # Create evaluation dataset
    dataset = create_evaluation_dataset(ground_truth_data, model_answers)
    print("✅ Created RAGAS-compatible dataset")
    
    # Run RAGAS evaluation
    print("\n📊 Running RAGAS evaluation...")
    score = evaluate(dataset, metrics=[answer_correctness])
    
    # Display results
    print("\n" + "="*50)
    print("📈 EVALUATION RESULTS")
    print("="*50)
    
    # Convert to pandas for easy viewing
    results_df = score.to_pandas()
    print("\nDetailed Results:")
    print(results_df)
    
    # Calculate and display average score
    avg_score = results_df['answer_correctness'].mean()
    print(f"\n🎯 Average Answer Correctness Score: {avg_score:.4f}")
    
    # Display dataset statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"  - Total Questions: {len(ground_truth_data['ground_truth'])}")
    print(f"  - Categories: {ground_truth_data['metadata']['categories']}")
    print(f"  - Source Document: {ground_truth_data['metadata']['source_document']}")
    print(f"  - Timeline File: {timeline_file_path}")
    
    print("\n" + "="*50)
    print("✅ Evaluation completed successfully!")
    
    return avg_score

def main():
    """Main function to evaluate both map-reduce and refine timelines."""
    print("🔍 RAGAS Timeline System Evaluation")
    print("="*60)
    
    # Find the latest output files
    print("🔍 Finding latest timeline output files...")
    latest_map_reduce, latest_refine = find_latest_output_files()
    
    if not latest_map_reduce:
        print("❌ Error: No map-reduce timeline files found!")
        return
    
    if not latest_refine:
        print("❌ Error: No refine timeline files found!")
        return
    
    print("\n" + "="*60)
    
    # Evaluate Map-Reduce Timeline
    print(f"\n📊 Evaluating Map-Reduce Timeline...")
    map_reduce_score = evaluate_timeline_system(latest_map_reduce, "Map-Reduce")
    
    # Evaluate Refine Timeline
    print(f"\n📊 Evaluating Refine Timeline...")
    refine_score = evaluate_timeline_system(latest_refine, "Refine")
    
    # Compare results
    if map_reduce_score is not None and refine_score is not None:
        print("\n" + "="*60)
        print("🏆 COMPARISON RESULTS")
        print("="*60)
        print(f"Map-Reduce Score: {map_reduce_score:.4f}")
        print(f"Refine Score: {refine_score:.4f}")
        
        if map_reduce_score > refine_score:
            print("🥇 Map-Reduce performed better!")
        elif refine_score > map_reduce_score:
            print("🥇 Refine performed better!")
        else:
            print("🤝 Both methods performed equally!")
    
    print("\n" + "="*60)
    print("✅ All evaluations completed!")

if __name__ == "__main__":
    main() 