# Data Directory

## Required File

Place the dataset file in this directory:

- **Filename**: `Dropout.xlsx`
- **Source**: [Specify your data source or institutional data]
- **Size**: ~4,400 student records
- **Format**: Excel (.xlsx)

## Data Description

The dataset contains student information including:

- **Demographics**: Age, gender, marital status, nationality
- **Academic Background**: Previous qualifications, admission grades
- **Family Background**: Parental education and occupation
- **Academic Performance**: Semester grades, units enrolled/approved
- **Financial Information**: Scholarship status, debtor status, tuition payment
- **Economic Indicators**: Unemployment rate, inflation rate, GDP
- **Target Variable**: Student status (Dropout, Graduate, Enrolled)

## Data Privacy

**Important**: This directory is excluded from version control via `.gitignore` to protect student privacy. Never commit raw data files containing personally identifiable information (PII).

## Getting Started

1. Place `Dropout.xlsx` in this directory
2. Run the Jupyter notebook: `student_dropout_prediction.ipynb`
3. The notebook will automatically load data from `data/Dropout.xlsx`

## Data Dictionary

For a detailed description of all features, see the main project README.
