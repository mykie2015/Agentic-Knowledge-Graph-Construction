# Domain Graph Constructor

A standalone Python script to build complete domain knowledge graphs from CSV data.

## Features

✅ **Complete Graph Construction**: Creates all nodes (Product, Assembly, Part, Supplier) and relationships (CONTAINS, IS_PART_OF, SUPPLIED_BY)

✅ **Robust Error Handling**: Graceful handling of missing files, connection issues, and data problems

✅ **Batch Processing**: Efficient batch creation of nodes and relationships

✅ **Verification**: Comprehensive graph verification with statistics and sample paths

✅ **Clean Output**: Clear progress indicators and detailed status messages

## Quick Usage

```bash
# Run the graph constructor
python construct_graph.py
```

## Expected Output

```
🚀 CONSTRUCTING COMPLETE DOMAIN GRAPH
============================================================
🧹 Clearing existing graph...
✅ Graph cleared successfully

📂 Loading CSV data...
✅ Loaded products.csv: 10 rows
✅ Loaded assemblies.csv: 64 rows
✅ Loaded parts.csv: 88 rows
✅ Loaded suppliers.csv: 20 rows

📊 Creating nodes...
  Creating Product nodes...
    ✅ Created 10 Product nodes
  Creating Assembly nodes...
    ✅ Created 64 Assembly nodes
  Creating Part nodes...
    ✅ Created 88 Part nodes
  Creating Supplier nodes...
    ✅ Created 20 Supplier nodes

✅ Total nodes created: 182

🔗 Creating relationships...
  Creating CONTAINS relationships...
    ✅ CONTAINS: 64 relationships
  Creating IS_PART_OF relationships...
    ✅ IS_PART_OF: 88 relationships
  Creating SUPPLIED_BY relationships...
    ✅ SUPPLIED_BY: 176 relationships

✅ Total relationships created: 328

🔍 VERIFYING CONSTRUCTED GRAPH
==================================================

📊 NODE STATISTICS:
  • Part: 88 nodes
  • Assembly: 64 nodes
  • Supplier: 20 nodes
  • Product: 10 nodes

🔗 RELATIONSHIP STATISTICS:
  • SUPPLIED_BY: 176 relationships
  • IS_PART_OF: 88 relationships
  • CONTAINS: 64 relationships

🌐 SAMPLE CONNECTED PATHS:
  Product → Assembly ← Part → Supplier:
    Uppsala Sofa → Seat Cushion ← Foam Insert → Nordic Foam Technologies
    Uppsala Sofa → Back Cushion ← Fabric Cover → Swedish Textiles Ltd
    Uppsala Sofa → Frame ← Metal Bracket → European Metal Works

============================================================
🎉 SUCCESS! Complete domain knowledge graph constructed!
   📊 Total nodes: 182
   🔗 Total relationships: 328
   🌐 Connected paths: 3

🔍 TO VISUALIZE IN NEO4J BROWSER:
   • Schema: CALL db.schema.visualization()
   • Sample: MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 25
============================================================
```

## What It Fixes

The script addresses the common issues:

1. **Missing Assembly Nodes**: Ensures all CSV files are properly loaded
2. **Broken Relationships**: Creates relationships in the correct order (nodes first, then relationships)
3. **Data Type Issues**: Proper string escaping and type handling
4. **Verification**: Confirms all parts of the graph are connected

## Script Structure

- **GraphConstructor Class**: Main class handling all graph operations
- **Error Handling**: Comprehensive error handling for each step
- **Modular Design**: Separate methods for nodes, relationships, and verification
- **Configurable**: Easy to modify data sources and construction rules

## Troubleshooting

If the script fails:

1. **Check CSV Files**: Ensure all CSV files exist in `../data/` directory
2. **Neo4j Connection**: Verify Neo4j is running and accessible
3. **Data Format**: Check CSV files have the expected columns
4. **Permissions**: Ensure write access to Neo4j database

## Integration

The script can be:
- **Run standalone** for quick graph construction
- **Imported as module** for use in other scripts
- **Modified** to handle different data sources
- **Extended** to support additional node types and relationships
