#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
import sys
import argparse
from collections import defaultdict
import re

def extract_symptoms(df):
    """
    Extract all unique symptoms from the dataframe.
    
    Args:
        df: DataFrame containing symptom data
        
    Returns:
        List of unique symptom texts
    """
    unique_symptom_texts = set()

    # Loop through each summary and extract text values
    for summary_str in df['summary'].fillna(""):
        try:
            # Parse the JSON string, handling single quotes
            summary = json.loads(summary_str.replace("'", '"'))
            
            # Extract text values from yes_symptoms array
            for item in summary.get("yes_symptoms", []):
                if "text" in item:
                    unique_symptom_texts.add(item["text"])
        except Exception:
            # Skip rows with invalid JSON
            continue

    return sorted(list(unique_symptom_texts))

def filter_symptoms_with_answers(df, symptom_list):
    """
    Filter symptoms to include only those with non-empty answers and exclude "การรักษาก่อนหน้า"
    
    Args:
        df: DataFrame containing symptom data
        symptom_list: List of symptoms to filter
        
    Returns:
        List of symptoms with answers
    """
    symptoms_with_answers = set()  # Use a set to avoid duplicates
    
    for symptom in symptom_list:
        if symptom != "การรักษาก่อนหน้า":
            has_answers = False
            for summary_str in df['summary'].fillna(""):
                try:
                    summary = json.loads(summary_str.replace("'", '"'))
                    for item in summary.get("yes_symptoms", []):
                        if (item.get("text") == symptom and 
                            item.get("answers") and 
                            any(a.strip() for a in item.get("answers", []))):
                            symptoms_with_answers.add(symptom)  # Use add() instead of append()
                            has_answers = True
                            break  # Found answers for this symptom
                    if has_answers:
                        break  # No need to check more summaries for this symptom
                except:
                    continue
    
    return sorted(list(symptoms_with_answers))  # Convert set back to sorted list
    
    return sorted(symptoms_with_answers)

def generate_recommendations_template(symptoms, output_path):
    """
    Generate a recommendations CSV template based on the symptom list.
    
    Args:
        symptoms: List of symptoms to include in the template
        output_path: Path to save the CSV file
        
    Returns:
        Path to the created file
    """
    # Create a DataFrame with the symptoms and empty recommendation columns
    df = pd.DataFrame({
        'อาการ': symptoms,
        'คำแนะนำเฉพาะทาง 1': ['พักผ่อนให้เพียงพอ'] * len(symptoms),
        'คำแนะนำเฉพาะทาง 2': ['ดื่มน้ำมากๆ'] * len(symptoms),
        'คำแนะนำเฉพาะทาง 3': ['หากอาการไม่ดีขึ้นหรือรุนแรงขึ้น ควรปรึกษาแพทย์'] * len(symptoms)
    })
    
    # Save to CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Created recommendations template at {output_path}")
    
    return output_path

def standardize_data(df):
    """Standardize data format for better consistency"""
    # Standardize "ประวัติ ATK" to "ประวัติATK" for consistency
    df["summary"] = df["summary"].str.replace("ประวัติ ATK", "ประวัติATK", regex=False)
    return df

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Preprocess symptom data and generate recommendations template")
    parser.add_argument("--file", type=str, help="Path to the Excel file containing symptom data")
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure assets directory exists
    assets_dir = os.path.join(current_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    print(f"Assets directory: {assets_dir}")
    
    # Use argument-provided file path if available, otherwise use default
    if args.file and os.path.isfile(args.file):
        excel_path = args.file
        print(f"Using specified file path: {excel_path}")
    else:
        excel_path = os.path.join(current_dir, "assets", "[CONFIDENTIAL] AI symptom picker data (Agnos candidate assignment).xlsx")
        print(f"Using default file path: {excel_path}")
        
        # If default file doesn't exist, try parent directory
        if not os.path.exists(excel_path):
            parent_excel_path = os.path.join(os.path.dirname(current_dir), 
                                            "[CONFIDENTIAL] AI symptom picker data (Agnos candidate assignment).xlsx")
            if os.path.exists(parent_excel_path):
                print(f"Default file not found, using parent directory file: {parent_excel_path}")
                excel_path = parent_excel_path
    
    # Define output CSV path in the assets directory
    csv_output_path = os.path.join(current_dir, "assets", "คำแนะนำเฉพาะทาง_56อาการ_อัปเดตใหม่.csv")
    
    # Check if Excel file exists
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found at {excel_path}")
        print(f"Please specify a valid file path using --file option")
        return False
        
    # Create assets directory if it doesn't exist
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    
    print(f"Loading data from {excel_path}...")
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)
        df['summary'] = df['summary'].fillna("")
        df['search_term'] = df['search_term'].fillna("")
        
        # Standardize data
        df = standardize_data(df)
        
        # Extract all unique symptoms
        print("Extracting unique symptoms...")
        all_symptoms = extract_symptoms(df)
        print(f"Found {len(all_symptoms)} unique symptoms")
        
        # Filter symptoms with answers
        print("Filtering symptoms with answers...")
        symptoms_with_answers = filter_symptoms_with_answers(df, all_symptoms)
        print(f"Found {len(symptoms_with_answers)} symptoms with answers")
        
        # Check if recommendations file exists
        if not os.path.exists(csv_output_path):
            print(f"Recommendations file not found at {csv_output_path}")
            print("Generating new recommendations template...")
            generate_recommendations_template(symptoms_with_answers, csv_output_path)
        else:
            print(f"Recommendations file already exists at {csv_output_path}")
            
        print("Preprocessing completed successfully.")
        return True
        
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return False

if __name__ == "__main__":
    print("Starting preprocessing script...")
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
