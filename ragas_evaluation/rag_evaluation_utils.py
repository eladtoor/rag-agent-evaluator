"""
RAG Evaluation Utilities

Shared utility functions for Context Precision, Context Recall, and Faithfulness evaluation.
Contains common data loading, dataset creation, and result handling functions.
"""

import json
import os
import sys
from datetime import datetime
from datasets import Dataset

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import RAG system components
try:
    from tools.rag_chain import step1_retrieval, rag_pipeline
    RAG_SYSTEM_AVAILABLE = True
except ImportError:
    print("⚠️  RAG system not available. Make sure tools/rag_chain.py exists.")
    RAG_SYSTEM_AVAILABLE = False

def load_rag_ground_truth():
    """
    Load the RAG ground truth dataset.
    
    Returns:
        dict: Ground truth data or None if not found
    """
    try:
        with open('results/ground_truth_dataset.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Loaded RAG ground truth with {len(data['ground_truth'])} questions")
            return data
    except FileNotFoundError:
        print("❌ Error: results/ground_truth_dataset.json not found!")
        print("Please create the RAG ground truth dataset first.")
        return None

def get_rag_response(question, top_k=3):
    """
    Get response from RAG system for a given question.
    
    Args:
        question (str): The question to ask
        top_k (int): Number of chunks to retrieve
        
    Returns:
        tuple: (answer, contexts) or (None, None) if error
    """
    if not RAG_SYSTEM_AVAILABLE:
        print("❌ RAG system not available")
        return None, None
    
    try:
        # Step 1: Retrieval - get relevant chunks
        chunks = step1_retrieval(question, use_reranking=False, top_k=top_k)
        
        if not chunks:
            print(f"⚠️  No chunks retrieved for question: {question}")
            return None, None
        
        # Step 2 & 3: Get full RAG response
        answer = rag_pipeline(question)
        
        # Extract text content from chunks for contexts
        contexts = []
        for chunk in chunks:
            if hasattr(chunk, 'page_content'):
                contexts.append(chunk.page_content)
            elif isinstance(chunk, dict) and 'content' in chunk:
                contexts.append(chunk['content'])
            elif isinstance(chunk, str):
                contexts.append(chunk)
            else:
                contexts.append(str(chunk))
        
        return answer, contexts
        
    except Exception as e:
        print(f"❌ Error getting RAG response for '{question}': {e}")
        return None, None

def extract_questions_and_answers(ground_truth_data):
    """
    Extract questions and ground truth answers from the dataset.
    
    Args:
        ground_truth_data (dict): The loaded ground truth dataset
        
    Returns:
        tuple: (questions, ground_truth_answers)
    """
    questions = [item["question"] for item in ground_truth_data["ground_truth"]]
    ground_truth_answers = [item["answer"] for item in ground_truth_data["ground_truth"]]
    
    return questions, ground_truth_answers

def collect_rag_responses(questions, top_k=3, max_questions=None):
    """
    Collect RAG responses for all questions.
    
    Args:
        questions (list): List of questions
        top_k (int): Number of chunks to retrieve
        max_questions (int): Limit number of questions (for testing)
        
    Returns:
        tuple: (rag_answers, all_contexts, successful_indices)
    """
    if max_questions:
        questions = questions[:max_questions]
        print(f"🔍 Processing first {max_questions} questions for evaluation")
    
    rag_answers = []
    all_contexts = []
    successful_indices = []
    
    print(f"\n🔄 Collecting RAG responses for {len(questions)} questions...")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. 🔍 Question: {question}")
        
        answer, contexts = get_rag_response(question, top_k=top_k)
        
        if answer and contexts:
            rag_answers.append(answer)
            all_contexts.append(contexts)
            successful_indices.append(i-1)  # 0-based index
            print(f"   ✅ Retrieved {len(contexts)} chunks")
        else:
            print(f"   ❌ Failed to get response")
    
    print(f"\n✅ Successfully collected {len(rag_answers)} responses out of {len(questions)} questions")
    
    return rag_answers, all_contexts, successful_indices

def create_ragas_dataset(questions, rag_answers, all_contexts, ground_truth_answers):
    """
    Create a RAGAS-compatible dataset.
    
    Args:
        questions (list): List of questions
        rag_answers (list): RAG system answers
        all_contexts (list): Retrieved contexts for each question
        ground_truth_answers (list): Expected answers
        
    Returns:
        Dataset: RAGAS-compatible dataset
    """
    if len(questions) != len(rag_answers) != len(all_contexts) != len(ground_truth_answers):
        raise ValueError("All input lists must have the same length")
    
    # Create dataset dictionary
    data_samples = {
        'question': questions,
        'answer': rag_answers,
        'contexts': all_contexts,
        'ground_truth': ground_truth_answers
    }
    
    dataset = Dataset.from_dict(data_samples)
    print(f"✅ Created RAGAS dataset with {len(dataset)} samples")
    
    return dataset

def save_evaluation_results(results, metric_name, additional_info=None):
    """
    Save evaluation results to JSON file.
    
    Args:
        results: RAGAS evaluation results
        metric_name (str): Name of the metric (e.g., 'context_precision')
        additional_info (dict): Additional information to save
    """
    # Ensure results directory exists
    os.makedirs("results", exist_ok=True)
    
    # Convert results to dict if needed
    if hasattr(results, 'to_pandas'):
        results_df = results.to_pandas()
        results_dict = results_df.to_dict('records')
        overall_score = results_df[metric_name].mean() if metric_name in results_df.columns else None
    else:
        results_dict = results
        overall_score = None
    
    # Create output structure
    output = {
        "metric_name": metric_name,
        "overall_score": overall_score,
        "evaluation_timestamp": datetime.now().isoformat(),
        "detailed_results": results_dict,
        "evaluation_type": "rag_evaluation"
    }
    
    # Add additional info if provided
    if additional_info:
        output.update(additional_info)
    
    # Save to file
    filename = f"results/{metric_name}_results.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    
    return filename

def display_evaluation_summary(results, metric_name):
    """
    Display a summary of evaluation results.
    
    Args:
        results: RAGAS evaluation results
        metric_name (str): Name of the metric
    """
    print(f"\n{'='*60}")
    print(f"📊 {metric_name.upper()} EVALUATION RESULTS")
    print(f"{'='*60}")
    
    if hasattr(results, 'to_pandas'):
        results_df = results.to_pandas()
        
        if metric_name in results_df.columns:
            overall_score = results_df[metric_name].mean()
            print(f"\n🎯 Overall {metric_name.replace('_', ' ').title()} Score: {overall_score:.4f}")
            
            # Show distribution
            print(f"\n📊 Score Distribution:")
            print(f"  - Min: {results_df[metric_name].min():.4f}")
            print(f"  - Max: {results_df[metric_name].max():.4f}")
            print(f"  - Std: {results_df[metric_name].std():.4f}")
            
            # Performance categories
            excellent = (results_df[metric_name] >= 0.8).sum()
            good = ((results_df[metric_name] >= 0.6) & (results_df[metric_name] < 0.8)).sum()
            fair = ((results_df[metric_name] >= 0.4) & (results_df[metric_name] < 0.6)).sum()
            poor = (results_df[metric_name] < 0.4).sum()
            
            print(f"\n📈 Performance Breakdown:")
            print(f"  - Excellent (≥0.8): {excellent} questions")
            print(f"  - Good (0.6-0.8): {good} questions")  
            print(f"  - Fair (0.4-0.6): {fair} questions")
            print(f"  - Poor (<0.4): {poor} questions")
        else:
            print(f"⚠️  Column '{metric_name}' not found in results")
    else:
        print("📊 Results summary not available")
    
    print(f"\n{'='*60}")

def check_rag_system_ready():
    """
    Check if the RAG system is ready for evaluation.
    
    Returns:
        bool: True if system is ready, False otherwise
    """
    if not RAG_SYSTEM_AVAILABLE:
        print("❌ RAG system not available")
        return False
    
    # Test with a simple question
    try:
        test_answer, test_contexts = get_rag_response("test question", top_k=1)
        if test_answer is None:
            print("❌ RAG system not responding properly")
            return False
        
        print("✅ RAG system is ready for evaluation")
        return True
        
    except Exception as e:
        print(f"❌ RAG system error: {e}")
        return False 