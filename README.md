# Patient Symptom Recommendation System

A Streamlit-based web application that helps medical professionals select symptoms and provide relevant follow-up questions and preliminary recommendations to patients.

## 📋 Features

- Interactive symptom selection with dropdown menus
- Categorized follow-up questions organized by type (duration, severity, location, etc.)
- Customized medical recommendations for each symptom
- Previous treatment history integration
- Symptom relationship analysis with visualizations
- Co-occurrence detection between different symptoms
- Easy-to-use web interface built with Streamlit

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- Excel file with symptom data in the specified format
- CSV file with recommendations (will be auto-generated if not present)

### Method 1: Using Conda (Recommended)

1. Create a new Conda environment:
```bash
conda create -n symptom-rec python=3.9
```

2. Activate the environment:
```bash
conda activate symptom-rec
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Method 2: Using Pip

1. Install required packages:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### 1. Data Preprocessing

First, run the preprocessing script to ensure data is properly formatted:

```bash
cd /path/to/recommendation_system_patient
python preprocess.py
```

You can also specify a custom Excel file path using the `--file` argument:

```bash
python preprocess.py --file "/path/to/your/excel/file.xlsx"
```

Important notes:
- Use quotes around the file path if it contains special characters (like spaces or square brackets)
- By default, the script looks for the Excel file in the `assets` directory
- If the default file is not found, it will check the parent directory

This script:
- Extracts unique symptoms from the Excel file
- Generates a recommendations template if not present
- Standardizes data formats for consistency

### 2. Running the Application

After preprocessing, start the Streamlit application:

```bash
streamlit run app.py
```

A web browser will automatically open with the application running at http://localhost:8501.

### 3. Using the Symptom Analyzer

The application includes a symptom relationship analysis feature that helps identify patterns in symptom co-occurrences:

1. Navigate to the symptom analysis section at the bottom of the application
2. Click "วิเคราะห์ข้อมูลอาการ" (Analyze Symptom Data) to generate visualizations
3. View the network graph showing how different symptoms relate to each other
4. Check the correlation table for detailed information on symptom co-occurrences

The analysis helps medical professionals identify potential symptom clusters that commonly appear together in patients.

## 📊 Project Structure

```
recommendation_system_patient/
├── app.py                 # Main Streamlit web application
├── data_processor.py      # Data processing functions module
├── symptom_analyzer.py    # Symptom relationship analysis module
├── preprocess.py          # Data preprocessing script
├── requirements.txt       # List of dependencies
├── assets/                # Data files folder
└── README.md              # This documentation
```

## 🔄 Customizing Data

You can customize the data sources in two ways:

### Method 1: Using the Web Interface

1. Open the application and use the sidebar settings
2. Uncheck "Use default data files"
3. Enter custom file paths for your symptom data and recommendations
4. Click "Reload Data" to apply changes

### Method 2: Direct File Replacement

Replace the files in the `assets` folder:
- Excel file: Contains patient symptom data with structured JSON responses
- CSV file: Contains symptom-specific medical recommendations

## ⚠️ Medical Disclaimer

- This system is intended to provide preliminary information only, not a medical diagnosis
- The recommendations are basic guidelines and should be verified by medical professionals
- In case of severe symptoms or medical emergencies, immediate professional medical attention should be sought