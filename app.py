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
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
# Check if symptom_analyzer module exists
try:
    from symptom_analyzer import analyze_symptoms
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False

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
    excel_path = os.path.join(current_dir, "assets", "[CONFIDENTIAL] AI symptom picker data (Agnos candidate assignment).xlsx")
    csv_path = os.path.join(current_dir, "assets", "คำแนะนำเฉพาะทาง_56อาการ_อัปเดตใหม่.csv")
    
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
        
        # Create analysis_output directory if not exists
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analysis_output = os.path.join(current_dir, "analysis_output")
        os.makedirs(analysis_output, exist_ok=True)
        
        # Navigation
        st.header("เมนู")
        app_mode = st.radio(
            "เลือกโหมดการใช้งาน:",
            ["อาการและคำแนะนำ", "วิเคราะห์ความสัมพันธ์อาการ"]
        )
        
        if st.button("โหลดข้อมูลใหม่"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    # Load data
    try:
        df, recommendations_dict = load_cached_data(excel_path, recommendations_path)
        
        # Extract symptoms
        symptoms = extract_all_symptoms(df)
        treatment_answers = get_treatment_answers(df)
        
        # Different app modes
        if app_mode == "อาการและคำแนะนำ":
            display_recommendation_interface(df, symptoms, treatment_answers, recommendations_dict)
        else:  # Symptom analysis mode
            display_symptom_analysis(df, excel_path, symptoms)
            
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
            
            # Display related symptoms if available
            try:
                related_symptoms_path = os.path.join("analysis_output", "symptom_relations.csv")
                if os.path.exists(related_symptoms_path):
                    related_df = pd.read_csv(related_symptoms_path)
                    if not related_df.empty:
                        symptom_row = related_df[related_df["อาการ"] == selected_symptom]
                        if not symptom_row.empty:
                            related_str = symptom_row.iloc[0]["อาการที่เกี่ยวข้อง"]
                            st.markdown("### 🔗 อาการที่มักพบร่วมกัน")
                            st.markdown(related_str)
            except Exception as e:
                # Silently handle errors reading related symptoms
                pass
                
        else:
            st.warning(f"ไม่พบข้อมูลเพิ่มเติมสำหรับอาการ '{selected_symptom}'")

def display_symptom_analysis(df, excel_path, symptoms):
    """Display symptom relationship analysis"""
    st.markdown("## 📊 วิเคราะห์ความสัมพันธ์ระหว่างอาการ")
    
    if not HAS_ANALYZER:
        st.error("ไม่พบโมดูล symptom_analyzer โปรดติดตั้งก่อนใช้งานส่วนนี้")
        return
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    analysis_output = os.path.join(current_dir, "analysis_output")
    
    # Check if analysis has been run
    network_image = os.path.join(analysis_output, "symptom_network.png")
    relations_csv = os.path.join(analysis_output, "symptom_relations.csv")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("วิเคราะห์ข้อมูลอาการ", type="primary"):
            with st.spinner("กำลังวิเคราะห์ข้อมูล..."):
                try:
                    # Run symptom analysis
                    analyze_symptoms(excel_path, analysis_output)
                    st.success("วิเคราะห์ข้อมูลเสร็จสิ้น!")
                    st.experimental_rerun()  # Refresh to show results
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์: {e}")
    
    with col2:
        st.markdown("""
        ระบบจะวิเคราะห์ความสัมพันธ์ระหว่างอาการต่างๆ จากข้อมูลผู้ป่วย โดย:
        - หาอาการที่มักพบร่วมกันบ่อย
        - สร้างแผนภาพความสัมพันธ์ (Network graph)
        - คำนวณความใกล้เคียงของอาการจากคำตอบที่เกี่ยวข้อง
        """)
    
    # Display results if available
    if os.path.exists(network_image) and os.path.exists(relations_csv):
        # Display network graph
        st.markdown("### แผนภาพความสัมพันธ์ระหว่างอาการ")
        st.markdown("ขนาดของวงกลม = ความถี่ของอาการ, ความหนาของเส้น = ความสัมพันธ์")
        st.image(network_image)
        
        # Display relations table
        st.markdown("### ตารางอาการที่สัมพันธ์กัน")
        
        try:
            relations_df = pd.read_csv(relations_csv)
            
            # Add search functionality
            search_symptom = st.selectbox("ค้นหาอาการ:", options=[""] + symptoms.copy())
            
            if search_symptom:
                filtered_df = relations_df[relations_df["อาการ"] == search_symptom]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(relations_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"ไม่สามารถแสดงข้อมูลความสัมพันธ์: {e}")
    else:
        st.info("ยังไม่มีผลการวิเคราะห์ กรุณากดปุ่ม 'วิเคราะห์ข้อมูลอาการ' เพื่อเริ่มการวิเคราะห์")

if __name__ == "__main__":
    main()
