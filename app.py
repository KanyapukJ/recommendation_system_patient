import streamlit as st
import pandas as pd
import os
import json
from data_processor import (
    load_data, 
    extract_all_symptoms, 
    get_answers_by_symptom,
    get_treatment_answers,
    group_answers
)

# Set page configuration
st.set_page_config(
    page_title="ระบบช่วยคัดกรองอาการเบื้องต้น",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS to improve the UI
st.markdown("""
<style>
    .stSelectbox label {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .recommendation-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
    }
    .recommendation-title {
        color: #4682b4;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .recommendation-item {
        margin-bottom: 8px;
        padding-left: 20px;
    }
    .warning-box {
        margin-top: 10px;
        padding: 8px 15px;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        color: #856404;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Define default paths
@st.cache_data
def get_default_paths():
    """Get default file paths based on the current working directory"""
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths to the data files
    excel_path = os.path.join(current_dir, "assets", "dataset.xlsx")
    csv_path = os.path.join(current_dir, "assets", "symptoms.csv")
    
    # Ensure the assets directory exists
    assets_dir = os.path.join(current_dir, "assets")
    if not os.path.exists(assets_dir):
        try:
            os.makedirs(assets_dir)
            print(f"Created assets directory: {assets_dir}")
        except Exception as e:
            print(f"Could not create assets directory: {e}")
    
    # Run preprocessing script if recommendation file doesn't exist
    if os.path.exists(excel_path) and not os.path.exists(csv_path):
        try:
            import subprocess
            preprocess_path = os.path.join(current_dir, "preprocess.py")
            if os.path.exists(preprocess_path):
                print("Running preprocessing script to generate recommendations file...")
                subprocess.run(["python", preprocess_path], check=True)
        except Exception as e:
            print(f"Error running preprocessing script: {e}")
    
    # Print paths for debugging
    print(f"Excel path: {excel_path}")
    print(f"CSV path: {csv_path}")
    
    return excel_path, csv_path

# Default recommendations
default_recommendations = [
    "พักผ่อนให้เพียงพอ",
    "ดื่มน้ำมากๆ",
    "หากอาการไม่ดีขึ้นหรือรุนแรงขึ้น ควรปรึกษาแพทย์"
]

# Load data
@st.cache_data
def load_cached_data(excel_path, recommendations_path):
    """Cache data loading to improve performance"""
    return load_data(excel_path, recommendations_path)

def main():
    # Set title
    st.title("🏥 ระบบช่วยคัดกรองอาการเบื้องต้น")
    
    # Sidebar for file paths and navigation
    with st.sidebar:
        st.header("ตั้งค่าข้อมูล")
        
        # Use default paths or allow custom paths
        default_excel_path, default_csv_path = get_default_paths()
        
        use_default = st.checkbox("ใช้ไฟล์ข้อมูลเริ่มต้น", value=True)
        
        if use_default:
            excel_path = default_excel_path
            recommendations_path = default_csv_path
        else:
            excel_path = st.text_input("ที่อยู่ไฟล์ Excel ข้อมูลอาการ", value=default_excel_path)
            recommendations_path = st.text_input("ที่อยู่ไฟล์ CSV คำแนะนำ", value=default_csv_path)
        
        # Navigation
        st.header("เมนู")
        
        if st.button("โหลดข้อมูลใหม่"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    # Load data
    try:
        df, recommendations_dict = load_cached_data(excel_path, recommendations_path)
        
        # Extract symptoms
        symptoms = extract_all_symptoms(df)
        treatment_answers = get_treatment_answers(df)
        
        # Display recommendation interface
        display_recommendation_interface(df, symptoms, treatment_answers, recommendations_dict)
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        st.info("โปรดตรวจสอบที่อยู่ไฟล์ข้อมูลในเมนูด้านซ้าย")

def display_recommendation_interface(df, symptoms, treatment_answers, recommendations_dict):
    """Display the main recommendation interface"""
    # Main interface
    st.markdown("### เลือกอาการที่ต้องการข้อมูลเพิ่มเติม")
    
    # Dropdown for symptom selection
    selected_symptom = st.selectbox(
        "อาการ:", 
        options=symptoms,
        format_func=lambda x: x,
        index=0 if symptoms else None
    )
    
    if selected_symptom:
        # Get answers for this symptom
        answers = get_answers_by_symptom(selected_symptom, df)
        
        if answers:
            grouped_answers = group_answers(answers)
            
            # Create columns for better layout
            st.markdown("### ข้อมูลเพิ่มเติมเกี่ยวกับอาการ")
            
            # Display each group in a separate expander
            for group_name, items in grouped_answers.items():
                with st.expander(f"{group_name}", expanded=True):
                    # Create a selectbox for each group
                    st.selectbox(
                        f"เลือก{group_name}:",
                        options=items,
                        key=f"dropdown_{group_name}"
                    )
            
            # Treatment history always displayed
            if treatment_answers:
                with st.expander("การรักษาก่อนหน้า", expanded=True):
                    st.selectbox(
                        "เลือกประวัติการรักษา:",
                        options=treatment_answers,
                        key="dropdown_treatment"
                    )
            
            # Recommendations
            st.markdown("### 💊 คำแนะนำเบื้องต้น")
            recs = recommendations_dict.get(selected_symptom, default_recommendations)
            
            for rec in recs:
                if rec and isinstance(rec, str):
                    st.markdown(f"- {rec}")
            
            # Warning message
            st.markdown(
                """
                <div class="warning-box">
                ⚠️ หากอาการไม่ดีขึ้นหรือรุนแรงขึ้น ควรรีบพบแพทย์
                </div>
                """, 
                unsafe_allow_html=True
            )
                
        else:
            st.warning(f"ไม่พบข้อมูลเพิ่มเติมสำหรับอาการ '{selected_symptom}'")

if __name__ == "__main__":
    main()
