# RAG Agent Evaluator

A LangChain-based agent system that performs both timeline summarization and Q&A over textbook data, evaluated using RAGAS with 4 core metrics.

## 🌟 Overview

This project processes a cybersecurity-themed textbook ("The Day Everything Slowed Down") and enables two intelligent tools for security analysts who struggle to extract clear, time-based insights from long unstructured incident reports.

### Key Features

- **✨ SummarizeTool**: Generates timeline summaries using both Refine and Map-Reduce methods
- **❓ RagQATool**: Answers questions using a Retrieval-Augmented Generation (RAG) system with ChromaDB and OpenAI embeddings
- **📊 RAGAS Evaluation**: Comprehensive evaluation using 4 core metrics for quality assessment

## 🎯 Problem Statement

Security analysts often struggle to:
- Extract clear, time-based insights from long unstructured incident reports
- Quickly understand the sequence of events in cybersecurity incidents
- Answer specific questions about complex security scenarios

## 💡 Our Solution

- **Automates summarization** into a timeline format
- **Supports Q&A** directly over raw text
- **Benchmarks quality** using LLM-based metrics
- **Provides structured insights** for security incident analysis

## 📋 Evaluation Metrics

The system is evaluated using RAGAS on the following metrics:

1. **Context Recall** - Measures how well the retrieval system finds relevant information
2. **Context Precision** - Evaluates the precision of retrieved context
3. **Faithfulness** - Assesses how faithful the generated answers are to the source material
4. **Answer Correctness** - Measures the overall correctness of generated answers

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Required dependencies (see installation section)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/eladtoor/rag-agent-evaluator
cd rag-agent-evaluator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Usage

#### Basic Usage

```python
from rag_agent_evaluator import RagAgent

# Initialize the agent
agent = RagAgent()

# Load your textbook data
agent.load_textbook("path/to/textbook.txt")

# Use the summarization tool
timeline_summary = agent.summarize_timeline()

# Use the Q&A tool
answer = agent.ask_question("What happened during the initial attack phase?")
```

#### Running Evaluation

```python
from rag_agent_evaluator import evaluate_system

# Run RAGAS evaluation
results = evaluate_system(
    questions=test_questions,
    ground_truths=ground_truth_answers,
    contexts=retrieved_contexts,
    answers=generated_answers
)

print(f"Context Recall: {results['context_recall']}")
print(f"Context Precision: {results['context_precision']}")
print(f"Faithfulness: {results['faithfulness']}")
print(f"Answer Correctness: {results['answer_correctness']}")
```

## 🏗️ Architecture

### Core Components

1. **Document Processing Pipeline**
   - Text chunking and preprocessing
   - Embedding generation using OpenAI embeddings
   - Vector storage in ChromaDB

2. **Agent Tools**
   - **SummarizeTool**: Timeline generation with dual approaches (Refine + Map-Reduce)
   - **RagQATool**: RAG-based question answering system

3. **Evaluation Framework**
   - RAGAS integration for automated evaluation
   - Comprehensive metrics reporting
   - Performance benchmarking

### Data Flow

```
Raw Textbook → Document Processing → Vector Store → Agent Tools → Evaluation
     ↓                ↓                    ↓           ↓           ↓
Text Chunks → Embeddings → ChromaDB → RAG/Summary → RAGAS Metrics
```

## 📊 Performance Metrics

The system provides detailed evaluation across multiple dimensions:

- **Retrieval Quality**: How well the system finds relevant information
- **Generation Quality**: Accuracy and faithfulness of generated content
- **Timeline Coherence**: Logical flow and completeness of timeline summaries
- **Answer Precision**: Correctness and relevance of Q&A responses

## 🛠️ Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=text-embedding-ada-002
```

### Customization Options

- **Chunking Strategy**: Adjust chunk size and overlap for optimal retrieval
- **Summarization Method**: Choose between Refine, Map-Reduce, or hybrid approaches
- **Evaluation Metrics**: Configure which RAGAS metrics to include
- **Model Selection**: Switch between different OpenAI models

## 📁 Project Structure

```
rag-agent-evaluator/
├── src/
│   ├── agents/          # Agent implementations
│   ├── tools/           # SummarizeTool and RagQATool
│   ├── evaluation/      # RAGAS evaluation framework
│   └── utils/           # Utility functions
├── data/
│   └── textbook/        # Sample textbook data
├── tests/               # Unit and integration tests
├── notebooks/           # Jupyter notebooks for exploration
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run evaluation benchmarks:

```bash
python scripts/run_evaluation.py --dataset data/textbook/test_set.json
```

## 📈 Results

The system demonstrates strong performance across all RAGAS metrics:

- **Context Recall**: Effective retrieval of relevant information
- **Context Precision**: High precision in context selection
- **Faithfulness**: Accurate representation of source material
- **Answer Correctness**: Reliable and accurate responses

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the agent framework
- **RAGAS** for evaluation metrics
- **ChromaDB** for vector storage
- **OpenAI** for embeddings and language models

## 📞 Contact

- **Author**: Elad Toorgeman
- **GitHub**: [@eladtoor](https://github.com/eladtoor)
- **Project Link**: [https://github.com/eladtoor/rag-agent-evaluator](https://github.com/eladtoor/rag-agent-evaluator)

## 🔮 Future Enhancements

- Support for additional document formats (PDF, DOCX)
- Integration with more vector databases
- Advanced evaluation metrics
- Multi-language support
- Real-time processing capabilities

---

**Built with ❤️ for the cybersecurity community**
