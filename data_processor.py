import pandas as pd
import json
import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional

def load_data(excel_path: str, recommendations_path: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Load the symptoms data from Excel and recommendations from CSV.
    
    Args:
        excel_path: Path to the Excel file with symptom data
        recommendations_path: Path to the CSV file with recommendations
        
    Returns:
        Tuple containing the DataFrame and recommendations dictionary
    """
    # Load main data
    df = pd.read_excel(excel_path)
    df["summary"] = df["summary"].fillna("")
    df["search_term"] = df["search_term"].fillna("")
    
    # Standardize "ประวัติ ATK" to "ประวัติATK" for consistency
    df["summary"] = df["summary"].str.replace("ประวัติ ATK", "ประวัติATK", regex=False)
    
    # Load recommendations
    try:
        recommendations_df = pd.read_csv(recommendations_path, encoding='utf-8')
        
        # Convert recommendations DataFrame to dictionary
        recommendations_dict = {}
        for index, row in recommendations_df.iterrows():
            symptom = row['อาการ']
            recs = [rec for rec in [row.get('คำแนะนำเฉพาะทาง 1', ''), 
                                   row.get('คำแนะนำเฉพาะทาง 2', ''), 
                                   row.get('คำแนะนำเฉพาะทาง 3', '')] 
                   if isinstance(rec, str) and rec.strip()]
            recommendations_dict[symptom] = recs
    except Exception as e:
        print(f"Error loading recommendations: {e}")
        recommendations_dict = {}
    
    return df, recommendations_dict


def extract_all_symptoms(df: pd.DataFrame) -> List[str]:
    """
    Extract all unique symptoms that have answers from the DataFrame.
    
    Args:
        df: DataFrame containing symptom data
        
    Returns:
        Sorted list of unique symptoms
    """
    symptoms = set()
    for summary_str in df['summary']:
        try:
            summary = json.loads(summary_str.replace("'", '"'))
            for item in summary.get("yes_symptoms", []):
                text = item.get("text", "").strip()
                answers = item.get("answers", [])
                if text and text != "การรักษาก่อนหน้า" and answers and any(a.strip() for a in answers):
                    symptoms.add(text)
        except:
            continue
    return sorted(symptoms)


def get_answers_by_symptom(symptom: str, df: pd.DataFrame) -> List[str]:
    """
    Get all unique answers associated with a specific symptom.
    
    Args:
        symptom: The symptom text to look for
        df: DataFrame containing symptom data
        
    Returns:
        List of unique answers for the symptom
    """
    all_answers = []
    for summary_str in df['summary']:
        try:
            summary = json.loads(summary_str.replace("'", '"'))
            for item in summary.get("yes_symptoms", []):
                if item.get("text", "").strip() == symptom:
                    answers = [a.strip() for a in item.get("answers", []) if a.strip()]
                    all_answers.extend(answers)
        except:
            continue
    return list(set(all_answers))  # Return unique answers


def get_treatment_answers(df: pd.DataFrame) -> List[str]:
    """
    Get all unique treatment history answers.
    
    Args:
        df: DataFrame containing symptom data
        
    Returns:
        List of unique treatment history answers
    """
    treatment_answers = set()
    for summary_str in df['summary']:
        try:
            summary = json.loads(summary_str.replace("'", '"'))
            for item in summary.get("yes_symptoms", []):
                if item.get("text", "").strip() == "การรักษาก่อนหน้า":
                    treatment_answers.update(a.strip() for a in item.get("answers", []) if a.strip())
        except:
            continue
    return sorted(treatment_answers)


def group_answers(answers: List[str]) -> Dict[str, List[str]]:
    """
    Group answers by their first word.
    
    Args:
        answers: List of answers to group
        
    Returns:
        Dictionary with groups as keys and lists of answers as values
    """
    groups = defaultdict(list)
    for ans in answers:
        parts = ans.split(' ', 1)
        if len(parts) > 1:
            key = parts[0]
        else:
            key = "อื่นๆ"
        groups[key].append(ans)
    return dict(sorted(groups.items()))  # Convert to regular dict for better serialization


def format_dropdown_options(items: List[str]) -> List[Tuple[str, str]]:
    """
    Format answers for dropdown display.
    
    Args:
        items: List of answer strings
        
    Returns:
        List of tuples (display_label, value)
    """
    options = []
    for item in sorted(items):
        parts = item.split(' ', 1)
        if len(parts) > 1:
            label = parts[1].replace(" ", "")  # Remove spaces from part after first space
        else:
            label = item  # No space found, use the whole text
        options.append((label, item))  # (label, value) pair
    return options
