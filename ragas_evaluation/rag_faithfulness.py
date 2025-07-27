"""
RAG Faithfulness Evaluation

Evaluates how factually accurate the generated answers are based on the retrieved context.
Faithfulness = (Number of claims in answer that can be inferred from context) / (Total claims in answer)

Simple, beginner-friendly implementation using shared utilities.
"""

from rag_evaluation_utils import (
    load_rag_ground_truth,
    extract_questions_and_answers,
    collect_rag_responses,
    create_ragas_dataset,
    save_evaluation_results,
    display_evaluation_summary,
    check_rag_system_ready
)

from ragas.metrics import faithfulness
from ragas import evaluate

def evaluate_faithfulness(max_questions=None, top_k=5):
    """
    Evaluate Faithfulness for RAG system.
    
    Args:
        max_questions (int): Limit number of questions for testing (None = all)
        top_k (int): Number of chunks to retrieve per question
    """
    print("🎯 RAG Faithfulness Evaluation")
    print("=" * 60)
    print("📊 Measuring how factually accurate generated answers are")
    print("=" * 60)
    
    # Step 1: Check if RAG system is ready
    if not check_rag_system_ready():
        print("❌ Cannot proceed - RAG system not ready")
        return None
    
    # Step 2: Load ground truth data
    ground_truth_data = load_rag_ground_truth()
    if not ground_truth_data:
        print("❌ Cannot proceed - ground truth not available")
        return None
    
    # Step 3: Extract questions and answers
    questions, ground_truth_answers = extract_questions_and_answers(ground_truth_data)
    
    if max_questions:
        questions = questions[:max_questions]
        ground_truth_answers = ground_truth_answers[:max_questions]
        print(f"🔍 Evaluating first {max_questions} questions")
    
    print(f"📝 Total questions to evaluate: {len(questions)}")
    
    # Step 4: Collect RAG responses
    rag_answers, all_contexts, successful_indices = collect_rag_responses(
        questions, 
        top_k=top_k
    )
    
    if not rag_answers:
        print("❌ No successful RAG responses - cannot evaluate")
        return None
    
    # Step 5: Filter data to only successful responses
    successful_questions = [questions[i] for i in successful_indices]
    successful_ground_truth = [ground_truth_answers[i] for i in successful_indices]
    
    print(f"✅ Successfully processed {len(successful_questions)} out of {len(questions)} questions")
    
    # Step 6: Create RAGAS dataset
    dataset = create_ragas_dataset(
        successful_questions,
        rag_answers, 
        all_contexts,
        successful_ground_truth
    )
    
    # Step 7: Run RAGAS evaluation
    print("\n📊 Running Faithfulness evaluation...")
    print("⏳ This may take a few minutes...")
    
    try:
        results = evaluate(dataset, metrics=[faithfulness])
        print("✅ Evaluation completed!")
        
        # Step 8: Display results
        display_evaluation_summary(results, "faithfulness")
        
        # Step 9: Save results
        additional_info = {
            "evaluation_config": {
                "top_k": top_k,
                "max_questions": max_questions,
                "total_questions_attempted": len(questions),
                "successful_questions": len(successful_questions)
            }
        }
        
        save_evaluation_results(results, "faithfulness", additional_info)
        
        return results
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None

def main():
    """Main function to run Faithfulness evaluation."""
    
    # Configuration
    MAX_QUESTIONS = None  # Set to 5 for quick testing, None for all questions
    TOP_K = 5            # Number of chunks to retrieve (balanced approach)
    
    print("🚀 Starting RAG Faithfulness Evaluation")
    print(f"⚙️  Configuration:")
    print(f"   - Max Questions: {MAX_QUESTIONS or 'All'}")
    print(f"   - Top K Chunks: {TOP_K}")
    print()
    
    # Run evaluation
    results = evaluate_faithfulness(
        max_questions=MAX_QUESTIONS,
        top_k=TOP_K
    )
    
    if results:
        print("\n🎉 Faithfulness evaluation completed successfully!")
        print("📁 Results saved to: results/faithfulness_results.json")
    else:
        print("\n❌ Faithfulness evaluation failed")

if __name__ == "__main__":
    main() 