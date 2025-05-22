# Patient Symptom Recommendation System

A Streamlit-based web application that helps medical professionals select symptoms and provide relevant follow-up questions and preliminary recommendations to patients.

## 📋 Features

- Interactive symptom selection with dropdown menus
- Categorized follow-up questions organized by type (duration, severity, location, etc.)
- Customized medical recommendations for each symptom
- Previous treatment history integration
- Easy-to-use web interface built with Streamlit

## 🔧 Installation

### Getting Started

1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/KanyapukJ/recommendation_system_patient.git
cd recommendation_system_patient
```

### Prerequisites

- Python 3.9 or higher
- **MANDATORY**: `assets` folder in the project root directory
- **MANDATORY**: Excel file with symptom data named `dataset.xlsx` (must be placed in the `assets` folder)
- **MANDATORY**: CSV file with recommendations named `symptoms.csv` (will be auto-generated in the `assets` folder by running `python preprocess.py --file "assets/dataset.xlsx"`)

### Using Conda (Recommended)

1. Create and activatea a Conda environment (recommended):
```bash
conda create -n symptom-rec python=3.9 -y
conda activate symptom-rec
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### 1. Data Preprocessing

First, ensure your data files are properly set up:

1. Make sure you have an `assets` folder in the root directory of the project
   ```bash
   mkdir -p assets
   ```

2. Place your Excel file with symptom data in the assets folder as `dataset.xlsx`:
   ```bash
   cp /path/to/your/excel/file.xlsx assets/dataset.xlsx
   ```

3. Run the preprocessing script to ensure data is properly formatted (this will generate the `symptoms.csv` file from your `dataset.xlsx`):
   ```bash
   python preprocess.py --file "assets/dataset.xlsx"
   ```
#### Using a Custom Excel File

If you want to use your own Excel file, simply provide its path with the `--file` argument when running the preprocessing script:

```bash
python preprocess.py --file "/path/to/your/custom/excel/file.xlsx"
```

You must copy and rename your file to `assets/dataset.xlsx` 

Important notes:
- Use quotes around the file path if it contains special characters (like spaces or square brackets)
- By default, the script looks for `dataset.xlsx` in the `assets` directory
- If the default file is not found, it will check the parent directory
- The output will be saved as `symptoms.csv` in the `assets` directory

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

## 📊 Project Structure

```
recommendation_system_patient/
├── app.py                 # Main Streamlit web application
├── data_processor.py      # Data processing functions module
├── preprocess.py          # Data preprocessing script
├── requirements.txt       # List of dependencies
├── assets/                # MANDATORY: Data files folder
│   └── dataset.xlsx       # MANDATORY: Default input file with symptom data
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

Replace the files in the `assets` folder (make sure to keep the exact filenames):
- `dataset.xlsx`: Contains patient symptom data with structured JSON responses
- `symptoms.csv`: Contains symptom-specific medical recommendations

## 📑 Dataset Structure

The `dataset.xlsx` file should have the following structure:

- Contains columns including at least `summary` which stores JSON data
- The JSON in the `summary` column has a `yes_symptoms` array containing:
  - `text`: The symptom name (e.g., "มีไข้", "ปวดหัว")
  - `answers`: Patient responses to follow-up questions about the symptom
- Other recommended columns: `search_term`, patient demographic information
- Each row represents a patient encounter or symptom report

## ⚠️ Medical Disclaimer

- This system is intended to provide preliminary information only, not a medical diagnosis
- The recommendations are basic guidelines and should be verified by medical professionals
- In case of severe symptoms or medical emergencies, immediate professional medical attention should be sought
