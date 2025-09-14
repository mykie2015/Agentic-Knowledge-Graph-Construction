# Agentic Knowledge Graph Construction

A production-ready multi-agent system for automated knowledge graph construction using Google's Agent Development Kit (ADK), Neo4j, and LLMs.

**Original Course Source**: https://www.deeplearning.ai/short-courses/agentic-knowledge-graph-construction/

## Overview

This repository contains a **fully implemented, production-ready** multi-agent system capable of constructing knowledge graphs from both structured (CSV) and unstructured (Markdown) data sources. The system features intelligent agents that can understand user intent, suggest files, propose schemas, and automatically construct comprehensive knowledge graphs.

**🎯 This is not just educational material** - it's a complete, working system that you can use for real knowledge graph construction projects!

## System Capabilities

- ✅ **Multi-Agent Architecture**: Four specialized agents working together seamlessly
- ✅ **Knowledge Graph Construction**: Transform structured and unstructured data into rich graph representations
- ✅ **Intelligent Schema Design**: Automatically propose and validate knowledge graph schemas
- ✅ **Entity Resolution**: Connect related entities across different data sources
- ✅ **User Intent Understanding**: Interpret and act on user requirements automatically
- ✅ **Neo4j Integration**: Full integration with graph databases for knowledge storage and retrieval
- ✅ **Production-Ready**: Complete logging, monitoring, and error handling

## System Architecture

### Core Agents (All Implemented ✅)
- **User Intent Agent**: Understands user goals and requirements for knowledge graph construction
- **File Suggestion Agent**: Analyzes available data and recommends relevant files
- **Schema Proposal Agent**: Designs comprehensive graph schemas from both structured and unstructured data
- **Knowledge Graph Constructor Agent**: Builds the actual knowledge graphs in Neo4j

### Educational Materials
The original course lessons (L3-L10) are preserved in `.spec-workflow/refer/` for reference:
- **L3-L4**: Google ADK foundations
- **L5-L8**: Individual agent development
- **L9-L10**: Knowledge graph construction techniques

## Sample Data

The system includes a realistic e-commerce dataset featuring:
- **Products**: Swedish furniture items (chairs, tables, desks, etc.)
- **Suppliers**: Component manufacturers and suppliers  
- **Parts & Assemblies**: Product composition data
- **Reviews**: Customer feedback in Markdown format

This data is organized in `data/input/` and serves as a comprehensive example for knowledge graph construction.

## Quick Start

### Prerequisites
- Python 3.8+
- Neo4j database (local or cloud)
- LLM API access (OpenAI, Anthropic, or local models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Agentic-Knowledge-Graph-Construction.git
   cd Agentic-Knowledge-Graph-Construction
   ```

2. **Set up virtual environment** (always use .venv as per cursor rules)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Create a `.env` file in the root directory:
   
   **For OpenAI API:**
   ```env
   OPENAI_API_KEY=sk-your_openai_api_key_here
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```
   
   **For local LLMs (Ollama, LM Studio, etc.):**
   ```env
   OPENAI_API_KEY=your_api_key_or_any_string
   OPENAI_BASE_URL=http://localhost:11434/v1
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```

4. **Set up Neo4j**
   - Install Neo4j Desktop or use Neo4j Aura
   - Ensure APOC plugin is installed
   - Start your database

### Running the System

```bash
# Check system status
python src/main.py status

# Start interactive session (recommended for first use)
python src/main.py interactive

# Process data in batch mode
python src/main.py batch data/input data/output

# View help
python src/main.py --help
```

## Key Technologies

- **Google ADK (Agent Development Kit)**: Framework for building multi-agent systems
- **Neo4j**: Graph database for knowledge storage
- **neo4j-graphrag**: Library for graph-based retrieval augmented generation
- **LiteLLM**: Universal LLM interface supporting multiple providers
- **Python**: Primary programming language

## Repository Structure

```
├── src/                           # 🎯 Production system code
│   ├── agents/                   # Multi-agent implementations
│   │   ├── user_intent_agent.py         # User goal understanding
│   │   ├── file_suggestion_agent.py     # File analysis & recommendation
│   │   ├── schema_proposal_agent.py     # Schema design (unified)
│   │   └── kg_constructor_agent.py      # Knowledge graph construction
│   ├── core/                     # Core system components
│   │   ├── agent_base.py         # Base agent class
│   │   └── session_manager.py    # Session & state management
│   ├── utils/                    # Utilities & tools
│   │   ├── config_manager.py     # Configuration management
│   │   ├── logging_config.py     # Structured logging
│   │   ├── neo4j_for_adk.py      # Neo4j integration
│   │   ├── helper.py             # ADK helper functions
│   │   └── tools.py              # Agent tools & utilities
│   └── main.py                   # 🚀 System entry point
├── data/                         # Data management
│   ├── input/                    # Source data (CSV, Markdown)
│   └── output/                   # Generated schemas, graphs, reports
├── log/                          # System logs
│   ├── agents/                   # Agent-specific logs
│   ├── system/                   # System logs
│   └── errors/                   # Error logs
├── config/                       # Configuration files
│   └── user-intent.md           # Agent configuration example
├── tests/                        # Test suite
│   ├── agents/                   # Agent tests
│   ├── config/                   # Configuration tests
│   └── utils/                    # Utility tests
└── .spec-workflow/               # Design & educational materials
    ├── specs/                    # System specifications
    └── refer/                    # Original course materials (L3-L10)
```

## Usage Examples

### 1. Basic Knowledge Graph Construction
```bash
# Check if everything is working
python src/main.py status

# Build a knowledge graph interactively
python src/main.py interactive
```

### 2. Batch Processing
```bash
# Process all data in data/input/
python src/main.py batch data/input data/output
```

### 3. Custom Configuration
```bash
# Use custom configuration
python src/main.py --config config/custom.yaml interactive
```

## System Features

### ✅ Production-Ready Capabilities
- **Automated Workflow**: End-to-end knowledge graph construction
- **Multi-Agent Coordination**: Intelligent agent collaboration
- **Schema Intelligence**: Automatic schema proposal from data analysis
- **Data Integration**: Handles both structured (CSV) and unstructured (Markdown) data
- **Graph Construction**: Direct Neo4j integration with optimized queries
- **Monitoring & Logging**: Comprehensive system observability
- **Error Recovery**: Graceful handling of failures
- **Configuration Management**: Flexible, environment-aware settings

### 🎓 Educational Value
While this is a production system, it maintains significant educational value:
- Clear agent separation demonstrating multi-agent architecture patterns
- Well-documented code showing ADK best practices
- Original course materials preserved for learning
- Comprehensive examples of knowledge graph construction techniques

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

## Documentation

- **[Setup Guide](SETUP_GUIDE.md)**: Comprehensive installation and configuration instructions
- **[Design Document](.spec-workflow/specs/agentic-kg-restructure/design.md)**: Technical architecture and design decisions
- **[Implementation Summary](AGENT_IMPLEMENTATION_SUMMARY.md)**: Complete overview of implemented features
- **[Cursor Rules](.cursorrules)**: Development guidelines and best practices

## Contributing

This is a production system that evolved from educational materials. Contributions welcome:
- **Bug Reports**: Report issues with system functionality
- **Feature Requests**: Suggest improvements or new capabilities  
- **Code Contributions**: Submit pull requests for enhancements
- **Documentation**: Help improve setup guides and system documentation
- **Educational Content**: Enhance the preserved course materials

## Performance & Scalability

The system is designed for production use with:
- **Async Operations**: Non-blocking agent operations
- **Session Management**: Efficient state handling
- **Connection Pooling**: Optimized database connections
- **Configurable Concurrency**: Adjustable performance parameters
- **Comprehensive Logging**: Performance monitoring and debugging

## Troubleshooting

### Common Issues
1. **Agent Initialization Errors**: Ensure `.venv` is activated and Google ADK is installed
2. **Neo4j Connection**: Verify database is running and credentials are correct
3. **LLM API Issues**: Check API keys and endpoint configuration
4. **Import Errors**: Run from project root and verify Python path

### Support
- Check the [Setup Guide](SETUP_GUIDE.md) for detailed instructions
- Review logs in `log/` directory for error details
- Run `python src/main.py status` to check system health

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Original Course**: DeepLearning.AI Agentic Knowledge Graph Construction
- **Framework**: Built using Google's Agent Development Kit
- **Database**: Powered by Neo4j graph database technology
- **Sample Data**: Inspired by Swedish furniture design
- **Development**: Enhanced with production-ready architecture and comprehensive tooling