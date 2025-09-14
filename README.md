# Agentic Knowledge Graph Construction

A comprehensive course on building multi-agent systems for automated knowledge graph construction using Google's Agent Development Kit (ADK), Neo4j, and LLMs.

source: https://www.deeplearning.ai/short-courses/agentic-knowledge-graph-construction/


## Overview

This repository contains a series of progressive lessons that teach you how to build intelligent agents capable of constructing knowledge graphs from both structured (CSV) and unstructured (Markdown) data sources. The course demonstrates how to create multi-agent systems that can understand user intent, suggest files, propose schemas, and automatically construct comprehensive knowledge graphs.

## What You'll Learn

- **Multi-Agent System Design**: Build teams of specialized agents using Google's ADK
- **Knowledge Graph Construction**: Transform structured and unstructured data into rich graph representations
- **Schema Design**: Automatically propose and validate knowledge graph schemas
- **Entity Resolution**: Connect related entities across different data sources
- **User Intent Understanding**: Create agents that can interpret and act on user requirements
- **Neo4j Integration**: Work with graph databases for knowledge storage and retrieval

## Course Structure

### Foundation Lessons
- **L3**: Introduction to Google's ADK - Part I (Basic agent creation and tools)
- **L4**: Introduction to Google's ADK - Part II (Agent teams and shared context)

### Core Agent Development
- **L5**: User Intent Agent (Understanding and processing user requirements)
- **L6**: File Suggestion Agent (Intelligent file recommendation)
- **L7**: Schema Proposal Agent for Structured Data (CSV schema generation)
- **L8**: Schema Proposal Agent for Unstructured Data (Markdown processing)

### Knowledge Graph Construction
- **L9**: Knowledge Graph Construction - Part I (Domain graph from CSV files)
- **L10**: Knowledge Graph Construction - Part II (Lexical and subject graphs from Markdown)

## Sample Data

The course includes a realistic e-commerce dataset featuring:
- **Products**: Swedish furniture items (chairs, tables, desks, etc.)
- **Suppliers**: Component manufacturers and suppliers
- **Parts & Assemblies**: Product composition data
- **Reviews**: Customer feedback in Markdown format

## Prerequisites

- Python 3.8+
- Basic understanding of graph databases
- Familiarity with LLMs and AI agents (helpful but not required)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Agentic-Knowledge-Graph-Construction.git
   cd Agentic-Knowledge-Graph-Construction
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   
   **For OpenAI API:**
   ```
   OPENAI_API_KEY=sk-your_openai_api_key_here
   ```
   
   **For OpenAI-Compatible APIs (Ollama, LM Studio, etc.):**
   ```
   OPENAI_API_KEY=your_api_key_or_any_string
   OPENAI_BASE_URL=http://localhost:11434/v1
   ```

4. **Set up Neo4j**
   - Install Neo4j Desktop or use Neo4j Aura
   - Configure connection details in the lesson notebooks

## Key Technologies

- **Google ADK (Agent Development Kit)**: Framework for building multi-agent systems
- **Neo4j**: Graph database for knowledge storage
- **neo4j-graphrag**: Library for graph-based retrieval augmented generation
- **LiteLLM**: Universal LLM interface supporting multiple providers
- **Python**: Primary programming language

## Repository Structure

```
├── data/                          # Sample datasets
│   ├── products.csv              # Product catalog
│   ├── suppliers.csv             # Supplier information
│   ├── parts.csv                 # Component data
│   ├── assemblies.csv            # Product assembly data
│   └── product_reviews/          # Customer reviews (Markdown)
├── L3-L10/                       # Course lessons
│   ├── *.ipynb                   # Jupyter notebooks
│   ├── helper.py                 # Utility functions
│   ├── tools.py                  # Agent tools
│   └── requirements.txt          # Lesson-specific dependencies
└── Appendix – Tips, Help, and Download/  # Additional resources
```

## Getting Started

1. Start with **L3** to understand the basics of Google's ADK
2. Progress through lessons sequentially - each builds on the previous
3. Follow the setup instructions in each lesson notebook
4. Experiment with the provided data or substitute your own

## Learning Outcomes

By completing this course, you'll be able to:
- Design and implement multi-agent systems for complex data processing tasks
- Build automated knowledge graph construction pipelines
- Create intelligent agents that can understand user intent and make recommendations
- Work with both structured and unstructured data sources
- Implement entity resolution and graph correlation techniques
- Deploy production-ready knowledge graph systems

## Testing

The project includes a comprehensive test suite organized under the `tests/` directory:

```bash
# Run system integration tests
python tests/test_imports.py

# Run specific test categories
python tests/agents/test_user_intent_config.py
python tests/config/test_config_parsing.py
```

All test files are preserved for debugging and validation purposes. See the [Setup Guide](SETUP_GUIDE.md) for detailed testing instructions.

## Contributing

This is an educational repository. Feel free to:
- Report issues or bugs
- Suggest improvements to the lessons
- Share your own implementations and extensions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built using Google's Agent Development Kit
- Powered by Neo4j graph database technology
- Sample data inspired by Swedish furniture design