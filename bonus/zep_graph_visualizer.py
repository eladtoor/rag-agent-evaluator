import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit not available, using matplotlib only")

class ZepGraphVisualizer:
    def __init__(self):
        """
        Initialize Zep graph visualizer
        """
        self.entities = []
        self.relationships = []
        self.graph = nx.Graph()
        
    def load_data(self):
        """
        Load entities and relationships from JSON files
        """
        # Try to load from JSON files
        json_files = ["zep_entities_results.json", "simple_entities_results.json"]
        
        for file_name in json_files:
            if os.path.exists(file_name):
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.entities = data.get('entities', [])
                    self.relationships = data.get('relationships', [])
                    print(f"✅ Loaded {len(self.entities)} entities and {len(self.relationships)} relationships from {file_name}")
                    return True
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
        
        return False
    
    def build_graph(self):
        """
        Build NetworkX graph from entities and relationships
        """
        # Add nodes (entities)
        for entity in self.entities:
            node_id = f"{entity['type']}_{entity['value']}"
            self.graph.add_node(node_id, 
                              label=entity['value'],
                              type=entity['type'],
                              confidence=entity.get('confidence', 0.8))
        
        # Add edges (relationships)
        for rel in self.relationships:
            source_id = f"{rel['source']}"
            target_id = f"{rel['target']}"
            
            # Find the actual node IDs
            source_node = None
            target_node = None
            
            for node in self.graph.nodes():
                if rel['source'].lower() in node.lower():
                    source_node = node
                if rel['target'].lower() in node.lower():
                    target_node = node
            
            if source_node and target_node:
                self.graph.add_edge(source_node, target_node,
                                  relationship=rel['relationship_type'],
                                  confidence=rel.get('confidence', 0.7))
        
        print(f"✅ Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def visualize_graph_matplotlib(self):
        """
        Visualize the graph using matplotlib
        """
        if not self.graph.nodes():
            print("No graph data to visualize")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Create layout
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Draw nodes by type
        node_colors = []
        node_sizes = []
        
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            node_type = node_data.get('type', 'UNKNOWN')
            
            # Color coding by entity type
            if node_type == 'PERSON':
                color = 'lightblue'
                size = 1000
            elif node_type == 'SYSTEM':
                color = 'lightgreen'
                size = 800
            elif node_type == 'TIME':
                color = 'lightcoral'
                size = 600
            elif node_type == 'LOCATION':
                color = 'lightyellow'
                size = 700
            else:
                color = 'lightgray'
                size = 500
            
            node_colors.append(color)
            node_sizes.append(size)
        
        # Draw the graph
        nx.draw(self.graph, pos, 
                node_color=node_colors,
                node_size=node_sizes,
                with_labels=True,
                font_size=8,
                font_weight='bold',
                edge_color='gray',
                alpha=0.7)
        
        # Add edge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'relationship')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=6)
        
        plt.title("Zep Graph Database - Entity Relationships", fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=10, label='PERSON'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=10, label='SYSTEM'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', markersize=10, label='TIME'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightyellow', markersize=10, label='LOCATION')
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        
        plt.tight_layout()
        plt.savefig('zep_graph_visualization.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Graph visualization saved as 'zep_graph_visualization.png'")
    
    def print_graph_stats(self):
        """
        Print statistics about the graph
        """
        if not self.graph.nodes():
            print("No graph data available")
            return
        
        print("\n" + "="*50)
        print("ZEP GRAPH DATABASE STATISTICS")
        print("="*50)
        
        print(f"Total Nodes (Entities): {self.graph.number_of_nodes()}")
        print(f"Total Edges (Relationships): {self.graph.number_of_edges()}")
        
        # Node types
        node_types = defaultdict(int)
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'UNKNOWN')
            node_types[node_type] += 1
        
        print(f"\nEntity Types:")
        for entity_type, count in node_types.items():
            print(f"  {entity_type}: {count}")
        
        # Relationship types
        edge_types = defaultdict(int)
        for edge in self.graph.edges():
            edge_data = self.graph.edges[edge]
            rel_type = edge_data.get('relationship', 'UNKNOWN')
            edge_types[rel_type] += 1
        
        print(f"\nRelationship Types:")
        for rel_type, count in edge_types.items():
            print(f"  {rel_type}: {count}")
        
        # Show some example relationships
        print(f"\nExample Relationships:")
        edge_count = 0
        for edge in self.graph.edges():
            if edge_count >= 5:  # Show only first 5
                break
            edge_data = self.graph.edges[edge]
            source_label = self.graph.nodes[edge[0]]['label']
            target_label = self.graph.nodes[edge[1]]['label']
            rel_type = edge_data.get('relationship', 'UNKNOWN')
            print(f"  {source_label} --[{rel_type}]--> {target_label}")
            edge_count += 1
    
    def interactive_graph_explorer(self):
        """
        Interactive graph exploration
        """
        if not self.graph.nodes():
            print("No graph data available")
            return
        
        print("\n" + "="*50)
        print("INTERACTIVE GRAPH EXPLORER")
        print("="*50)
        
        while True:
            print(f"\nAvailable commands:")
            print("- 'nodes': Show all nodes")
            print("- 'edges': Show all edges")
            print("- 'neighbors <node>': Show neighbors of a node")
            print("- 'path <node1> <node2>': Find path between nodes")
            print("- 'stats': Show graph statistics")
            print("- 'quit': Exit")
            
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'nodes':
                print("\nAll Nodes:")
                for node in self.graph.nodes():
                    node_data = self.graph.nodes[node]
                    print(f"  {node_data['label']} ({node_data['type']})")
            elif command == 'edges':
                print("\nAll Edges:")
                for edge in self.graph.edges():
                    edge_data = self.graph.edges[edge]
                    source_label = self.graph.nodes[edge[0]]['label']
                    target_label = self.graph.nodes[edge[1]]['label']
                    rel_type = edge_data.get('relationship', 'UNKNOWN')
                    print(f"  {source_label} --[{rel_type}]--> {target_label}")
            elif command.startswith('neighbors '):
                node_name = command[10:].strip()
                found = False
                for node in self.graph.nodes():
                    if node_name.lower() in self.graph.nodes[node]['label'].lower():
                        print(f"\nNeighbors of {self.graph.nodes[node]['label']}:")
                        for neighbor in self.graph.neighbors(node):
                            neighbor_data = self.graph.nodes[neighbor]
                            edge_data = self.graph.edges[node, neighbor]
                            rel_type = edge_data.get('relationship', 'UNKNOWN')
                            print(f"  {neighbor_data['label']} ({neighbor_data['type']}) --[{rel_type}]")
                        found = True
                        break
                if not found:
                    print(f"Node '{node_name}' not found")
            elif command.startswith('path '):
                parts = command.split()
                if len(parts) >= 3:
                    node1_name = parts[1]
                    node2_name = parts[2]
                    
                    # Find nodes
                    node1 = None
                    node2 = None
                    for node in self.graph.nodes():
                        if node1_name.lower() in self.graph.nodes[node]['label'].lower():
                            node1 = node
                        if node2_name.lower() in self.graph.nodes[node]['label'].lower():
                            node2 = node
                    
                    if node1 and node2:
                        try:
                            path = nx.shortest_path(self.graph, node1, node2)
                            print(f"\nPath from {self.graph.nodes[node1]['label']} to {self.graph.nodes[node2]['label']}:")
                            for i, node in enumerate(path):
                                node_data = self.graph.nodes[node]
                                print(f"  {i+1}. {node_data['label']} ({node_data['type']})")
                        except nx.NetworkXNoPath:
                            print(f"No path found between {node1_name} and {node2_name}")
                    else:
                        print("One or both nodes not found")
                else:
                    print("Usage: path <node1> <node2>")
            elif command == 'stats':
                self.print_graph_stats()
            else:
                print("Unknown command")

def main():
    """
    Main function to run the Zep graph visualizer
    """
    print("="*60)
    print("Zep Graph Database Visualizer")
    print("="*60)
    
    visualizer = ZepGraphVisualizer()
    
    # Load data
    if not visualizer.load_data():
        print("❌ Could not load data. Make sure to run entity extraction first.")
        return
    
    # Build graph
    visualizer.build_graph()
    
    # Print statistics
    visualizer.print_graph_stats()
    
    # Visualize graph
    print("\nGenerating graph visualization...")
    visualizer.visualize_graph_matplotlib()
    
    # Interactive exploration
    print("\nStarting interactive graph explorer...")
    visualizer.interactive_graph_explorer()

if __name__ == "__main__":
    main() 