"""
RAG Context Recall Evaluation

Evaluates how well the retrieval system captures all relevant information needed to answer a question.
Context Recall = (Relevant information retrieved) / (Total relevant information in document)

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

from ragas.metrics import context_recall
from ragas import evaluate

def evaluate_context_recall(max_questions=None, top_k=3):
    """
    Evaluate Context Recall for RAG system.
    
    Args:
        max_questions (int): Limit number of questions for testing (None = all)
        top_k (int): Number of chunks to retrieve per question
    """
    print("🎯 RAG Context Recall Evaluation")
    print("=" * 60)
    print("📊 Measuring how well we capture all relevant information")
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
    print("\n📊 Running Context Recall evaluation...")
    print("⏳ This may take a few minutes...")
    
    try:
        results = evaluate(dataset, metrics=[context_recall])
        print("✅ Evaluation completed!")
        
        # Step 8: Display results
        display_evaluation_summary(results, "context_recall")
        
        # Step 9: Save results
        additional_info = {
            "evaluation_config": {
                "top_k": top_k,
                "max_questions": max_questions,
                "total_questions_attempted": len(questions),
                "successful_questions": len(successful_questions)
            }
        }
        
        save_evaluation_results(results, "context_recall", additional_info)
        
        return results
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None

def main():
    """Main function to run Context Recall evaluation."""
    
    # Configuration
    MAX_QUESTIONS = None    # Set to None for all questions
    TOP_K = 2           # Number of chunks to retrieve (testing higher for 50%+ recall)
    
    print("🚀 Starting RAG Context Recall Evaluation")
    print(f"⚙️  Configuration:")
    print(f"   - Max Questions: {MAX_QUESTIONS or 'All'}")
    print(f"   - Top K Chunks: {TOP_K}")
    print()
    
    # Run evaluation
    results = evaluate_context_recall(
        max_questions=MAX_QUESTIONS,
        top_k=TOP_K
    )
    
    if results:
        print("\n🎉 Context Recall evaluation completed successfully!")
        print("📁 Results saved to: results/context_recall_results.json")
    else:
        print("\n❌ Context Recall evaluation failed")

if __name__ == "__main__":
    main() 