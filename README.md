# rag-agent-evaluator

A LangChain-based agent system that performs both **timeline summarization** and **Q&A over textbook data**, evaluated using **RAGAS** with 4 core metrics.

---

## 📚 What This Project Does

This project processes a cybersecurity-themed textbook ("The Day Everything Slowed Down") and enables two intelligent tools:

- ✨ `SummarizeTool`: Generates a timeline summary using both **Refine** and **Map-Reduce** methods  
- ❓ `RagQATool`: Answers questions using a Retrieval-Augmented Generation (RAG) system with ChromaDB and OpenAI embeddings

The system is evaluated using **RAGAS** on the following metrics:
- `Context Recall`
- `Context Precision`
- `Faithfulness`
- `Answer Correctness`

---

## 💼 Business Problem

Security analysts often struggle to extract clear, time-based insights from long unstructured incident reports.  
Our solution:
- Automates summarization into a timeline
- Supports Q&A directly over raw text
- Benchmarks quality using LLM-based metrics

---

## 🛠️ How to Run

1. Clone the repo
```bash
git clone https://github.com/eladtoor/rag-agent-evaluator
cd rag-agent-evaluator
