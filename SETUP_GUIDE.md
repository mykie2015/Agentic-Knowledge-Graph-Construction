# Setup Guide: Restructured Agentic Knowledge Graph Construction System

## Overview

This guide will help you set up and run the restructured Agentic Knowledge Graph Construction system. The system has been transformed from educational notebooks into a production-ready, modular multi-agent architecture.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Neo4j database (local or cloud)
- Access to LLM API (OpenAI, Anthropic, or local models)
- 8GB RAM minimum, 16GB recommended
- 10GB free disk space

### Required Services

#### 1. Neo4j Database
**Option A: Neo4j Desktop (Recommended for development)**
```bash
# Download from https://neo4j.com/download/
# Create a new database with:
# - Database name: neo4j (or your preferred name)
# - Password: your_secure_password
# - APOC plugin installed
```

**Option B: Neo4j Aura (Cloud)**
```bash
# Sign up at https://neo4j.com/cloud/aura/
# Create a free instance
# Note down connection details
```

**Option C: Docker**
```bash
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/your_password \
    --env NEO4J_PLUGINS='["apoc"]' \
    neo4j:latest
```

#### 2. LLM API Access
**Option A: OpenAI**
```bash
# Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B: Local Models (Ollama)**
```bash
# Install Ollama: https://ollama.ai/
ollama serve
# In another terminal:
ollama pull llama2  # or your preferred model
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="ollama"  # any string works for local
```

## Installation

### 1. Clone and Setup Repository
```bash
git clone <your-repo-url>
cd Agentic-Knowledge-Graph-Construction
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install -r src/requirements.txt

# Note: Google ADK may need special installation
# Check https://github.com/google/agent-development-kit for latest instructions
```

### 4. Environment Configuration
Create a `.env` file in the project root:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
NEO4J_IMPORT_DIR=./data/input

# LLM Configuration
OPENAI_API_KEY=sk-your-openai-key
# OPENAI_BASE_URL=http://localhost:11434/v1  # Uncomment for local models

# System Configuration
LOG_LEVEL=INFO
LOG_DIR=./log
INPUT_DIR=./data/input
OUTPUT_DIR=./data/output
MAX_CONCURRENT_AGENTS=3
```

### 5. Verify Installation
```bash
python test_imports.py
```

Expected output:
```
🚀 Testing Restructured Agentic Knowledge Graph Construction System
======================================================================
🧪 Testing imports...
  ✅ Utils imports successful
  ✅ Core imports successful
  ✅ Agent imports successful
  ✅ Main module imports successful

🧪 Testing basic functionality...
  ✅ Configuration manager working
  ✅ Neo4j connection working
  ✅ User Intent Agent: healthy

======================================================================
✅ All tests passed! System is ready for use.
```

## Usage

### Interactive Mode
Start an interactive session with the agents:
```bash
cd src
python main.py interactive
```

Example session:
```
🤖 Welcome to the Agentic Knowledge Graph Construction system!
You: I want to build a knowledge graph of our furniture products
🤖 I understand you want to create a furniture product knowledge graph...
```

### Batch Mode
Process data automatically:
```bash
cd src
python main.py batch ../data/input ../data/output
```

### System Status
Check system health:
```bash
cd src
python main.py status
```

## Configuration

### Agent Configuration

#### System Configuration
Create `config.yaml`:
```yaml
agents:
  user_intent:
    enabled: true
    model: "openai/gpt-4o"
    max_retries: 3
    conversation_style: "casual"      # formal, casual, educational, efficient
    domain_specialization: "general"  # business, research, technical, general
    validation_strictness: "moderate" # strict, moderate, permissive
  
  file_suggestion:
    enabled: true
    model: "openai/gpt-4o"
    max_retries: 3
  
  kg_constructor:
    enabled: true
    batch_size: 1000

neo4j:
  uri: "bolt://localhost:7687"
  username: "neo4j"
  password: "your_password"

logging:
  level: "INFO"
  enable_json: true
```

#### Agent-Specific Configuration
The User Intent Agent uses a dedicated configuration file:
- **Location**: `config/user-intent.md`
- **Format**: Markdown with embedded configuration
- **Customizable Elements**:
  - System prompt and behavior guidelines
  - Valid graph types
  - Validation rules and criteria
  - Conversation flow examples
  - Error handling responses

**Example customization**:
```bash
# Edit the agent's behavior
vim config/user-intent.md

# The agent will automatically reload configuration
cd src
python main.py interactive
```

Use custom config:
```bash
cd src
python main.py --config ../config.yaml interactive
```

## Data Preparation

### Input Data Structure
```
data/input/
├── csv/
│   ├── products.csv      # Required columns: product_id, product_name
│   ├── suppliers.csv     # Required columns: supplier_id, name
│   ├── parts.csv         # Required columns: part_id, part_name
│   └── assemblies.csv    # Required columns: assembly_id, assembly_name
└── markdown/
    └── product_reviews/  # Customer reviews and descriptions
        ├── product1_reviews.md
        └── product2_reviews.md
```

### Sample Data
The system includes sample furniture data:
- Products: Swedish-style furniture items
- Suppliers: Component manufacturers
- Parts & Assemblies: Product structure
- Reviews: Customer feedback

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure you're running from the src directory
cd src
python main.py status

# Or add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python test_imports.py
```

#### 2. Neo4j Connection Failed
```bash
# Check Neo4j status
neo4j status  # For local installation

# Verify connection details
neo4j-admin test-connection --uri bolt://localhost:7687 --username neo4j

# Check environment variables
echo $NEO4J_URI
echo $NEO4J_USERNAME
```

#### 3. LLM API Issues
```bash
# Test OpenAI connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# For local models, ensure Ollama is running
curl http://localhost:11434/api/tags
```

#### 4. Permission Errors
```bash
# Ensure log and output directories are writable
chmod 755 log data/output

# Check file permissions
ls -la data/input/csv/
```

### Debug Mode
Enable debug logging:
```bash
cd src
python main.py --debug interactive
```

## Architecture Overview

### Directory Structure
```
src/
├── agents/              # Multi-agent implementations
│   ├── user_intent_agent.py
│   ├── file_suggestion_agent.py
│   └── kg_constructor_agent.py
├── core/               # Core system components
│   ├── agent_base.py
│   └── session_manager.py
├── utils/              # Utilities and tools
│   ├── config_manager.py
│   ├── logging_config.py
│   ├── neo4j_for_adk.py
│   ├── helper.py
│   └── tools.py
└── main.py            # Entry point

log/                   # Structured logging
├── agents/           # Agent-specific logs
├── system/           # System logs
└── errors/           # Error logs

data/                 # Data management
├── input/           # Source data
└── output/          # Generated outputs
```

### Agent Workflow
1. **User Intent Agent**: Understands goals and requirements
2. **File Suggestion Agent**: Recommends relevant data files
3. **Schema Proposal Agents**: Design graph schemas (future)
4. **KG Constructor Agent**: Builds the actual knowledge graph

## Development

### Adding New Agents
1. Inherit from `BaseAgent`
2. Implement required methods
3. Add to main.py
4. Update configuration

### Custom Tools
Add new tools to `utils/tools.py` following the pattern:
```python
def my_custom_tool(tool_context: ToolContext, param: str) -> Dict[str, Any]:
    try:
        # Tool implementation
        return tool_success("result", data)
    except Exception as e:
        return tool_error(f"Error: {e}")
```

### Testing

The project includes a comprehensive test suite organized under the `tests/` directory:

```
tests/
├── __init__.py                    # Main tests package
├── test_imports.py               # System integration tests
├── agents/                       # Agent-specific tests
│   ├── __init__.py
│   └── test_user_intent_config.py
├── config/                       # Configuration tests
│   ├── __init__.py
│   └── test_config_parsing.py
├── core/                         # Core functionality tests
│   └── __init__.py
└── utils/                        # Utility function tests
    └── __init__.py
```

#### Running Tests

```bash
# Run system integration tests
python tests/test_imports.py

# Run specific test categories
python tests/agents/test_user_intent_config.py
python tests/config/test_config_parsing.py

# Test specific agents manually
cd src
python -c "from agents.user_intent_agent import UserIntentAgent; print(UserIntentAgent().health_check())"

# Test configuration loading
cd src
python -c "from utils.config_manager import get_config; print('Config loaded:', bool(get_config()))"
```

#### Test Development Guidelines

- All test files should be saved under the `tests/` folder
- Follow the naming convention: `test_<functionality>.py`
- Organize tests in subdirectories matching the source structure
- Test files are preserved for debugging and validation purposes
- Use the `.cursorrules` file for additional development guidelines

## Production Deployment

### Docker Deployment
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    environment:
      NEO4J_AUTH: neo4j/production_password
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - ./data/input:/var/lib/neo4j/import

  kg-system:
    build: .
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_PASSWORD: production_password
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - neo4j
    volumes:
      - ./data:/app/data
      - ./log:/app/log

volumes:
  neo4j_data:
```

### Environment Variables
```bash
# Production environment
export NEO4J_URI="bolt://production-neo4j:7687"
export NEO4J_PASSWORD="secure_production_password"
export OPENAI_API_KEY="production_api_key"
export LOG_LEVEL="WARNING"
export MAX_CONCURRENT_AGENTS="5"
```

## Support

### Documentation
- **Requirements**: `.spec-workflow/specs/agentic-kg-restructure/requirements.md`
- **Design**: `.spec-workflow/specs/agentic-kg-restructure/design.md`
- **Summary**: `RESTRUCTURE_SUMMARY.md`

### Logs
Check logs for troubleshooting:
```bash
# System logs
tail -f log/system/system.log

# Agent logs
tail -f log/agents/agents.log

# Error logs
tail -f log/errors/errors.log
```

### Health Checks
Monitor system health:
```bash
cd src
python main.py status
```

Expected healthy output:
```
✅ Configuration loaded
✅ Neo4j connection working
✅ User Intent Agent healthy
✅ File Suggestion Agent healthy
✅ KG Constructor Agent healthy
✅ Input directory accessible
✅ Output directory accessible
```
