#!/usr/bin/env python3
"""
Domain Knowledge Graph Constructor

This script builds a complete domain knowledge graph from CSV data files.
It creates nodes (Product, Assembly, Part, Supplier) and relationships 
(CONTAINS, IS_PART_OF, SUPPLIED_BY) in Neo4j.

Usage:
    python construct_graph.py
"""

import pandas as pd
from neo4j_for_adk import graphdb
from typing import Dict, Any
import os
import sys


class GraphConstructor:
    """Handles the construction of domain knowledge graphs from CSV data."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the graph constructor.
        
        Args:
            data_dir: Directory containing CSV files. Defaults to ../data
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.data_dir = data_dir
        
        # Define construction plan
        self.construction_plan = {
            "Product": {
                "file": "products.csv",
                "label": "Product", 
                "unique_property": "product_id", 
                "properties": ["product_name", "price", "description"]
            },
            "Assembly": {
                "file": "assemblies.csv",
                "label": "Assembly", 
                "unique_property": "assembly_id", 
                "properties": ["assembly_name", "quantity", "product_id"]
            }, 
            "Part": {
                "file": "parts.csv",
                "label": "Part", 
                "unique_property": "part_id", 
                "properties": ["part_name", "quantity", "assembly_id"]
            }, 
            "Supplier": {
                "file": "suppliers.csv",
                "label": "Supplier", 
                "unique_property": "supplier_id", 
                "properties": ["name", "specialty", "city", "country", "website", "contact_email"]
            }
        }
    
    def create_constraint(self, label: str, property_key: str) -> bool:
        """Create a uniqueness constraint for a node type."""
        try:
            constraint_name = f"{label}_{property_key}_constraint"
            query = f"""CREATE CONSTRAINT `{constraint_name}` IF NOT EXISTS
            FOR (n:`{label}`)
            REQUIRE n.`{property_key}` IS UNIQUE"""
            
            result = graphdb.send_query(query)
            return result['status'] == 'success'
        except Exception as e:
            print(f"❌ Error creating constraint for {label}: {e}")
            return False
    
    def load_csv_data(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files into DataFrames."""
        csv_data = {}
        
        for node_type, config in self.construction_plan.items():
            file_path = os.path.join(self.data_dir, config['file'])
            
            if not os.path.exists(file_path):
                print(f"❌ CSV file not found: {file_path}")
                continue
                
            try:
                df = pd.read_csv(file_path)
                csv_data[node_type.lower()] = df
                print(f"✅ Loaded {config['file']}: {len(df)} rows")
            except Exception as e:
                print(f"❌ Error loading {config['file']}: {e}")
        
        return csv_data
    
    def create_nodes(self, df: pd.DataFrame, label: str, unique_property: str, properties: list) -> int:
        """Create nodes from DataFrame data."""
        print(f"  Creating {label} nodes...")
        
        # Create constraint
        if not self.create_constraint(label, unique_property):
            print(f"    ⚠️ Warning: Could not create constraint for {label}")
        
        nodes_created = 0
        batch_size = 50
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            merge_statements = []
            
            for _, row in batch.iterrows():
                props = []
                
                # Include unique property and all other properties
                for prop in [unique_property] + properties:
                    if prop in row and pd.notna(row[prop]):
                        value = row[prop]
                        if isinstance(value, str):
                            # Escape quotes and handle special characters
                            value = str(value).replace('"', '\\"').replace("'", "\\'")
                            props.append(f'{prop}: "{value}"')
                        else:
                            props.append(f'{prop}: {value}')
                
                if props:  # Only create if we have properties
                    prop_string = ", ".join(props)
                    merge_statements.append(f"MERGE (:{label} {{{prop_string}}})")
            
            # Execute batch
            if merge_statements:
                batch_query = "\n".join(merge_statements)
                try:
                    result = graphdb.send_query(batch_query)
                    if result['status'] == 'success':
                        nodes_created += len(merge_statements)
                    else:
                        print(f"    ❌ Batch error: {result.get('error_message', 'Unknown')}")
                except Exception as e:
                    print(f"    ❌ Exception in batch: {e}")
        
        print(f"    ✅ Created {nodes_created} {label} nodes")
        return nodes_created
    
    def create_relationships(self) -> Dict[str, int]:
        """Create all relationships between nodes."""
        print("\n🔗 Creating relationships...")
        
        relationships_created = {}
        
        # 1. Product CONTAINS Assembly
        print("  Creating CONTAINS relationships...")
        contains_query = """
        MATCH (p:Product), (a:Assembly)
        WHERE a.product_id = p.product_id
        MERGE (p)-[r:CONTAINS]->(a)
        SET r.created_at = datetime()
        RETURN count(r) as created
        """
        
        try:
            result = graphdb.send_query(contains_query)
            if result['status'] == 'success':
                count = result['query_result'][0]['created']
                relationships_created['CONTAINS'] = count
                print(f"    ✅ CONTAINS: {count} relationships")
            else:
                print(f"    ❌ CONTAINS error: {result.get('error_message', 'Unknown')}")
        except Exception as e:
            print(f"    ❌ CONTAINS exception: {e}")
        
        # 2. Part IS_PART_OF Assembly
        print("  Creating IS_PART_OF relationships...")
        part_of_query = """
        MATCH (part:Part), (a:Assembly)
        WHERE part.assembly_id = a.assembly_id
        MERGE (part)-[r:IS_PART_OF]->(a)
        SET r.created_at = datetime()
        RETURN count(r) as created
        """
        
        try:
            result = graphdb.send_query(part_of_query)
            if result['status'] == 'success':
                count = result['query_result'][0]['created']
                relationships_created['IS_PART_OF'] = count
                print(f"    ✅ IS_PART_OF: {count} relationships")
            else:
                print(f"    ❌ IS_PART_OF error: {result.get('error_message', 'Unknown')}")
        except Exception as e:
            print(f"    ❌ IS_PART_OF exception: {e}")
        
        # 3. Part SUPPLIED_BY Supplier
        print("  Creating SUPPLIED_BY relationships...")
        supplier_query = """
        MATCH (part:Part), (supplier:Supplier)
        WITH part, supplier
        ORDER BY part.part_id, supplier.supplier_id
        WITH part, collect(supplier)[0..1] as suppliers
        UNWIND suppliers as supplier
        MERGE (part)-[r:SUPPLIED_BY]->(supplier)
        SET r.created_at = datetime()
        RETURN count(r) as created
        """
        
        try:
            result = graphdb.send_query(supplier_query)
            if result['status'] == 'success':
                count = result['query_result'][0]['created']
                relationships_created['SUPPLIED_BY'] = count
                print(f"    ✅ SUPPLIED_BY: {count} relationships")
            else:
                print(f"    ❌ SUPPLIED_BY error: {result.get('error_message', 'Unknown')}")
        except Exception as e:
            print(f"    ❌ SUPPLIED_BY exception: {e}")
        
        return relationships_created
    
    def verify_graph(self) -> Dict[str, Any]:
        """Verify the constructed graph and return statistics."""
        print("\n🔍 VERIFYING CONSTRUCTED GRAPH")
        print("=" * 50)
        
        verification_results = {
            'nodes': {},
            'relationships': {},
            'connected_paths': []
        }
        
        # Check node counts
        try:
            node_result = graphdb.send_query("""
            MATCH (n) 
            RETURN labels(n)[0] as node_type, count(n) as count 
            ORDER BY count DESC
            """)
            
            if node_result['status'] == 'success':
                print("\n📊 NODE STATISTICS:")
                total_nodes = 0
                for stat in node_result['query_result']:
                    node_type = stat['node_type']
                    count = stat['count']
                    verification_results['nodes'][node_type] = count
                    total_nodes += count
                    print(f"  • {node_type}: {count} nodes")
                verification_results['total_nodes'] = total_nodes
        except Exception as e:
            print(f"❌ Error checking nodes: {e}")
        
        # Check relationship counts
        try:
            rel_result = graphdb.send_query("""
            MATCH ()-[r]-() 
            RETURN type(r) as relationship_type, count(r) as count 
            ORDER BY count DESC
            """)
            
            if rel_result['status'] == 'success':
                print("\n🔗 RELATIONSHIP STATISTICS:")
                total_rels = 0
                for stat in rel_result['query_result']:
                    rel_type = stat['relationship_type']
                    count = stat['count']
                    verification_results['relationships'][rel_type] = count
                    total_rels += count
                    print(f"  • {rel_type}: {count} relationships")
                verification_results['total_relationships'] = total_rels
        except Exception as e:
            print(f"❌ Error checking relationships: {e}")
        
        # Test connected paths
        try:
            path_result = graphdb.send_query("""
            MATCH (p:Product)-[:CONTAINS]->(a:Assembly)<-[:IS_PART_OF]-(part:Part)-[:SUPPLIED_BY]->(s:Supplier)
            RETURN p.product_name, a.assembly_name, part.part_name, s.name
            LIMIT 3
            """)
            
            if path_result['status'] == 'success' and path_result['query_result']:
                print("\n🌐 SAMPLE CONNECTED PATHS:")
                print("  Product → Assembly ← Part → Supplier:")
                for path in path_result['query_result']:
                    path_str = f"{path['p.product_name']} → {path['a.assembly_name']} ← {path['part.part_name']} → {path['s.name']}"
                    verification_results['connected_paths'].append(path_str)
                    print(f"    {path_str}")
            else:
                print("\n🌐 SAMPLE CONNECTED PATHS:")
                print("  ❌ No complete connected paths found")
        except Exception as e:
            print(f"❌ Error checking paths: {e}")
        
        return verification_results
    
    def construct_complete_graph(self, clear_existing: bool = True) -> bool:
        """Main method to construct the complete domain graph."""
        print("🚀 CONSTRUCTING COMPLETE DOMAIN GRAPH")
        print("=" * 60)
        
        # Clear existing graph if requested
        if clear_existing:
            print("🧹 Clearing existing graph...")
            try:
                clear_result = graphdb.send_query("MATCH (n) DETACH DELETE n")
                if clear_result['status'] == 'success':
                    print("✅ Graph cleared successfully")
                else:
                    print(f"⚠️ Warning: {clear_result.get('error_message', 'Could not clear graph')}")
            except Exception as e:
                print(f"❌ Error clearing graph: {e}")
                return False
        
        # Load CSV data
        print("\n📂 Loading CSV data...")
        csv_data = self.load_csv_data()
        
        if not csv_data:
            print("❌ No CSV data loaded. Cannot proceed.")
            return False
        
        # Create all nodes
        print("\n📊 Creating nodes...")
        total_nodes_created = 0
        
        for node_type, config in self.construction_plan.items():
            df_key = node_type.lower()
            if df_key in csv_data:
                nodes_created = self.create_nodes(
                    csv_data[df_key],
                    config['label'],
                    config['unique_property'],
                    config['properties']
                )
                total_nodes_created += nodes_created
            else:
                print(f"  ⚠️ No data found for {node_type}")
        
        print(f"\n✅ Total nodes created: {total_nodes_created}")
        
        # Create all relationships
        relationships_created = self.create_relationships()
        total_rels = sum(relationships_created.values())
        print(f"\n✅ Total relationships created: {total_rels}")
        
        # Verify the graph
        verification = self.verify_graph()
        
        # Final summary
        print(f"\n{'=' * 60}")
        success = (
            verification.get('total_nodes', 0) > 0 and 
            verification.get('total_relationships', 0) > 0 and
            len(verification.get('connected_paths', [])) > 0
        )
        
        if success:
            print("🎉 SUCCESS! Complete domain knowledge graph constructed!")
            print(f"   📊 Total nodes: {verification.get('total_nodes', 0)}")
            print(f"   🔗 Total relationships: {verification.get('total_relationships', 0)}")
            print(f"   🌐 Connected paths: {len(verification.get('connected_paths', []))}")
            
            print("\n🔍 TO VISUALIZE IN NEO4J BROWSER:")
            print("   • Schema: CALL db.schema.visualization()")
            print("   • Sample: MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 25")
        else:
            print("❌ Graph construction incomplete!")
            if verification.get('total_nodes', 0) == 0:
                print("   • No nodes created - check CSV files and data directory")
            if verification.get('total_relationships', 0) == 0:
                print("   • No relationships created - check node properties match")
            if len(verification.get('connected_paths', [])) == 0:
                print("   • No connected paths - relationships may be incomplete")
        
        print(f"{'=' * 60}")
        return success


def main():
    """Main entry point for the script."""
    try:
        # Test Neo4j connection
        print("🔌 Testing Neo4j connection...")
        test_result = graphdb.send_query("RETURN 'Connection successful!' as message")
        if test_result['status'] != 'success':
            print("❌ Cannot connect to Neo4j. Please check your configuration.")
            sys.exit(1)
        print("✅ Neo4j connection successful")
        
        # Create graph constructor
        constructor = GraphConstructor()
        
        # Build the complete graph
        success = constructor.construct_complete_graph(clear_existing=True)
        
        if success:
            print("\n🎊 Graph construction completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Graph construction failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
