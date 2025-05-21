#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import json
import numpy as np
from collections import defaultdict, Counter
import networkx as nx
from typing import List, Dict, Tuple, Set
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_symptom_combinations(df: pd.DataFrame) -> List[Set[str]]:
    """
    Extract combinations of symptoms that appear together in patient records.
    
    Args:
        df: DataFrame containing symptom data
        
    Returns:
        List of sets, where each set contains symptoms that appeared together
    """
    symptom_combinations = []
    
    for summary_str in df['summary'].fillna(""):
        try:
            summary = json.loads(summary_str.replace("'", '"'))
            symptoms_in_record = set()
            
            for item in summary.get("yes_symptoms", []):
                symptom = item.get("text", "").strip()
                if symptom and symptom != "การรักษาก่อนหน้า":
                    symptoms_in_record.add(symptom)
            
            if len(symptoms_in_record) > 1:  # Only consider records with multiple symptoms
                symptom_combinations.append(symptoms_in_record)
                
        except Exception:
            continue
            
    return symptom_combinations

def calculate_symptom_cooccurrence(symptom_combinations: List[Set[str]]) -> pd.DataFrame:
    """
    Calculate co-occurrence matrix for symptoms.
    
    Args:
        symptom_combinations: List of sets containing symptoms that appeared together
        
    Returns:
        DataFrame representing co-occurrence matrix
    """
    # Count co-occurrences
    all_symptoms = set()
    for combo in symptom_combinations:
        all_symptoms.update(combo)
    
    all_symptoms = sorted(list(all_symptoms))
    cooccurrence_matrix = pd.DataFrame(0, index=all_symptoms, columns=all_symptoms)
    
    # Fill the co-occurrence matrix
    for combo in symptom_combinations:
        for symptom1 in combo:
            for symptom2 in combo:
                if symptom1 != symptom2:
                    cooccurrence_matrix.loc[symptom1, symptom2] += 1
    
    return cooccurrence_matrix

def find_most_related_symptoms(cooccurrence_matrix: pd.DataFrame, top_n: int = 5) -> Dict[str, List[Tuple[str, int]]]:
    """
    Find the most related symptoms for each symptom.
    
    Args:
        cooccurrence_matrix: Co-occurrence matrix of symptoms
        top_n: Number of top related symptoms to return
        
    Returns:
        Dictionary mapping each symptom to its most related symptoms
    """
    related_symptoms = {}
    
    for symptom in cooccurrence_matrix.index:
        # Get related symptoms sorted by co-occurrence count
        related = [(other_symptom, count) 
                  for other_symptom, count in cooccurrence_matrix[symptom].items() 
                  if count > 0 and other_symptom != symptom]
        
        # Sort by count (descending)
        related.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N
        related_symptoms[symptom] = related[:top_n]
    
    return related_symptoms

def create_symptom_graph(cooccurrence_matrix: pd.DataFrame, min_weight: int = 2) -> nx.Graph:
    """
    Create a network graph of symptom relationships.
    
    Args:
        cooccurrence_matrix: Co-occurrence matrix of symptoms
        min_weight: Minimum co-occurrence count to include an edge
        
    Returns:
        NetworkX graph object
    """
    G = nx.Graph()
    
    # Add nodes
    for symptom in cooccurrence_matrix.index:
        G.add_node(symptom)
    
    # Add edges with weights
    for symptom1 in cooccurrence_matrix.index:
        for symptom2 in cooccurrence_matrix.columns:
            weight = cooccurrence_matrix.loc[symptom1, symptom2]
            if weight >= min_weight and symptom1 != symptom2:
                G.add_edge(symptom1, symptom2, weight=weight)
    
    return G

def plot_symptom_network(G: nx.Graph, filename: str = 'symptom_network.png', 
                         figsize: Tuple[int, int] = (12, 10), 
                         node_size_factor: float = 100) -> None:
    """
    Plot and save a visualization of the symptom network.
    
    Args:
        G: NetworkX graph of symptoms
        filename: Output file path
        figsize: Figure size as (width, height)
        node_size_factor: Factor to multiply node degrees by for sizing
    """
    plt.figure(figsize=figsize)
    
    # Calculate node sizes based on degree
    node_sizes = [G.degree(node) * node_size_factor for node in G.nodes()]
    
    # Calculate edge weights for thickness
    edge_weights = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]
    
    # Use spring layout for positioning
    pos = nx.spring_layout(G, seed=42)
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, alpha=0.8, 
                          node_color='skyblue', edgecolors='gray')
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.5, edge_color='gray')
    
    # Labels with smaller font
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def calculate_symptom_similarity(df: pd.DataFrame, symptoms: List[str]) -> pd.DataFrame:
    """
    Calculate symptom similarity based on their associated answers.
    
    Args:
        df: DataFrame containing symptom data
        symptoms: List of symptom names
        
    Returns:
        DataFrame containing symptom similarity matrix
    """
    # Extract all answers for each symptom
    symptom_answers = {}
    for symptom in symptoms:
        answers = []
        for summary_str in df['summary'].fillna(""):
            try:
                summary = json.loads(summary_str.replace("'", '"'))
                for item in summary.get("yes_symptoms", []):
                    if item.get("text", "").strip() == symptom:
                        answers.extend([a.strip() for a in item.get("answers", []) if a.strip()])
            except:
                continue
        
        # Join all answers into a single text document for this symptom
        symptom_answers[symptom] = " ".join(answers)
    
    # Use CountVectorizer to convert text to numerical features
    vectorizer = CountVectorizer(analyzer='word', token_pattern=r'\b\w+\b')
    
    # Create feature vectors for symptoms with answers
    valid_symptoms = [s for s in symptoms if symptom_answers[s]]
    if len(valid_symptoms) < 2:
        return pd.DataFrame()  # Not enough symptoms with answers
        
    answer_texts = [symptom_answers[s] for s in valid_symptoms]
    X = vectorizer.fit_transform(answer_texts)
    
    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(X)
    
    # Create DataFrame from similarity matrix
    sim_df = pd.DataFrame(similarity_matrix, index=valid_symptoms, columns=valid_symptoms)
    
    return sim_df

def export_symptom_relations(related_symptoms: Dict[str, List[Tuple[str, int]]], 
                            output_path: str) -> None:
    """
    Export symptom relationships to a CSV file.
    
    Args:
        related_symptoms: Dictionary of related symptoms
        output_path: Path to save the CSV file
    """
    # Convert to DataFrame
    rows = []
    for symptom, related in related_symptoms.items():
        related_str = "; ".join([f"{r[0]} ({r[1]})" for r in related])
        rows.append({
            "อาการ": symptom,
            "อาการที่เกี่ยวข้อง": related_str
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Exported symptom relations to {output_path}")

def analyze_symptoms(excel_path, output_dir):
    """
    Run a complete symptom analysis.
    
    Args:
        excel_path: Path to the Excel data file
        output_dir: Directory to save output files
    """
    import os
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    df = pd.read_excel(excel_path)
    df['summary'] = df['summary'].fillna("")
    
    # Extract symptoms that appear together
    print("Extracting symptom combinations...")
    symptom_combinations = extract_symptom_combinations(df)
    print(f"Found {len(symptom_combinations)} patient records with multiple symptoms")
    
    # Calculate co-occurrence
    print("Calculating symptom co-occurrences...")
    cooccurrence_matrix = calculate_symptom_cooccurrence(symptom_combinations)
    cooccurrence_matrix.to_csv(os.path.join(output_dir, "symptom_cooccurrence.csv"))
    
    # Find related symptoms
    print("Finding related symptoms...")
    related_symptoms = find_most_related_symptoms(cooccurrence_matrix)
    export_symptom_relations(related_symptoms, os.path.join(output_dir, "symptom_relations.csv"))
    
    # Create and save network graph
    print("Creating symptom network visualization...")
    G = create_symptom_graph(cooccurrence_matrix)
    plot_symptom_network(G, os.path.join(output_dir, "symptom_network.png"))
    
    # Calculate symptom similarity based on answers
    print("Calculating symptom similarity based on answers...")
    symptoms = sorted(list(cooccurrence_matrix.index))
    similarity_matrix = calculate_symptom_similarity(df, symptoms)
    if not similarity_matrix.empty:
        similarity_matrix.to_csv(os.path.join(output_dir, "symptom_similarity.csv"))
    
    print("Symptom analysis completed successfully!")
    return {
        "cooccurrence_matrix": cooccurrence_matrix,
        "related_symptoms": related_symptoms,
        "graph": G,
        "similarity_matrix": similarity_matrix
    }

if __name__ == "__main__":
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze symptom relationships")
    parser.add_argument("--file", type=str, help="Path to the Excel file containing symptom data")
    parser.add_argument("--output", type=str, help="Directory to save output files")
    args = parser.parse_args()
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Use provided paths or defaults
    excel_path = args.file if args.file else os.path.join(
        current_dir, "assets", "[CONFIDENTIAL] AI symptom picker data (Agnos candidate assignment).xlsx")
    output_dir = args.output if args.output else os.path.join(current_dir, "analysis_output")
    
    analyze_symptoms(excel_path, output_dir)
