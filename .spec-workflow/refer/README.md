# Course Reference Materials

This directory contains the original educational course materials from the "Agentic Knowledge Graph Construction" course. These files have been moved here to maintain the clean restructured project while preserving the educational content for reference.

## Original Course Structure

### Lesson Directories
- **L3/**: Introduction to Google's ADK - Part I (Basic agent creation and tools)
- **L4/**: Introduction to Google's ADK - Part II (Agent teams and shared context)
- **L5/**: User Intent Agent (Understanding and processing user requirements)
- **L6/**: File Suggestion Agent (Intelligent file recommendation)
- **L7/**: Schema Proposal Agent for Structured Data (CSV schema generation)
- **L8/**: Schema Proposal Agent for Unstructured Data (Markdown processing)
- **L9/**: Knowledge Graph Construction - Part I (Domain graph from CSV files)
- **L10/**: Knowledge Graph Construction - Part II (Lexical and subject graphs from Markdown)

### Additional Materials
- **Appendix – Tips, Help, and Download/**: Course appendix with helpful resources and images
- **debug_wentuo.py**: Debug utility from the original course
- **helper.py**: Original helper functions (now integrated into restructured system)
- **original_requirements.txt**: Original course dependencies

## Course Data
The course used sample data including:
- **Products**: Swedish furniture items (chairs, tables, desks, etc.)
- **Suppliers**: Component manufacturers and suppliers
- **Parts & Assemblies**: Product composition data
- **Reviews**: Customer feedback in Markdown format

This data has been reorganized and is now available in the main `data/input/` directory of the restructured system.

## Integration with Restructured System

The restructured system builds upon the concepts and functionality from these lessons:

### Concept Mapping
| Original Lesson | Restructured Component |
|----------------|----------------------|
| L3-L4 (ADK Basics) | `src/core/agent_base.py`, `src/utils/helper.py` |
| L5 (User Intent) | `src/agents/user_intent_agent.py` |
| L6 (File Suggestion) | `src/agents/file_suggestion_agent.py` |
| L7-L8 (Schema Proposal) | Planned agents (see tasks.md) |
| L9-L10 (KG Construction) | `src/agents/kg_constructor_agent.py` |

### Code Reuse
- **Neo4j Integration**: Enhanced from L9's `neo4j_for_adk.py`
- **Agent Tools**: Extended from various lesson `tools.py` files
- **Helper Functions**: Integrated and enhanced in the new system
- **Construction Logic**: Adapted from L9's `construct_graph.py`

## Educational Value

These materials remain valuable for:
- Understanding the step-by-step learning progression
- Seeing example implementations and notebook-based exploration
- Reference for specific ADK patterns and techniques
- Debugging and troubleshooting the restructured system

## Usage Notes

To run any of the original lesson notebooks:
1. Navigate to the specific lesson directory
2. Install the lesson-specific requirements
3. Follow the lesson instructions

Example:
```bash
cd .spec-workflow/refer/L9
pip install -r requirements.txt
jupyter notebook kg_construction_1.ipynb
```

Note: The restructured system in the main `src/` directory provides the same functionality in a production-ready format.
