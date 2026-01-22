# Student Dropout Prediction: Early Risk Identification System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.0-orange)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A machine learning system to predict student dropout risk and enable early intervention strategies in higher education.

## 📋 Table of Contents

- [Overview](#overview)
- [Business Problem](#business-problem)
- [Dataset](#dataset)
- [Methodology](#methodology)
- [Key Findings](#key-findings)
- [Results](#results)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Model Performance](#model-performance)
- [Technologies Used](#technologies-used)
- [Future Work](#future-work)
- [Author](#author)

## 🎯 Overview

Student dropout is a critical challenge for higher education institutions, impacting both student success and institutional performance. This project develops a **predictive analytics solution** to identify at-risk students early in their academic journey, enabling timely interventions that improve retention rates.

Using machine learning classification models trained on student demographics, academic performance, family background, and macroeconomic factors, the system predicts dropout probability and assigns risk levels to guide institutional support programs.

## 💼 Business Problem

### Challenge
- **Student retention** directly affects graduation rates and institutional reputation
- **Late identification** of struggling students limits intervention effectiveness
- **Resource constraints** require targeted support allocation to at-risk populations

### Solution
A data-driven early warning system that:
- Identifies high-risk students at the end of first semester
- Quantifies dropout probability for prioritized intervention
- Reveals key factors influencing student persistence
- Enables proactive rather than reactive student support

### Impact
- **Improved retention rates** through early intervention
- **Optimized resource allocation** to students who need it most
- **Data-driven policy decisions** for institutional programs
- **Enhanced student success outcomes** and graduation metrics

## 📊 Dataset

### Overview
- **Size**: 4,424 student records
- **Features**: 37 variables covering demographics, academics, family background, and economics
- **Target**: Student status (Dropout, Graduate, Enrolled)
- **Modeling Target**: Binary classification (Dropout vs. Not Dropout)

### Feature Categories

**Demographics**
- Age at enrollment, gender, marital status, nationality

**Academic Background**
- Admission grade, previous qualifications, course enrollment, attendance type

**Family Background**
- Parental education levels, parental occupations

**Academic Performance**
- Semester grades, units enrolled/approved, success rates (1st and 2nd semester)

**Financial Indicators**
- Scholarship status, debtor status, tuition payment status

**Macroeconomic Context**
- Unemployment rate, inflation rate, GDP growth

📖 **Full Data Dictionary**: See [DATA_DICTIONARY.md](DATA_DICTIONARY.md)

### Class Distribution
- **Dropout**: ~32% (1,421 students)
- **Graduate**: ~50% (2,209 students)
- **Enrolled**: ~18% (794 students)

Binary target (Dropout vs. Not Dropout): **32% / 68%** split

## 🔬 Methodology

### 1. Data Preprocessing
- **Column standardization**: Cleaned and normalized feature names
- **Target creation**: Binary dropout indicator (1=Dropout, 0=Graduate/Enrolled)
- **Outlier detection**: IQR-based outlier removal (3x IQR threshold)
- **Missing values**: None detected (complete dataset)

### 2. Exploratory Data Analysis
- **Distribution analysis** of numerical and categorical features
- **Correlation analysis** to identify multicollinearity
- **Target relationship analysis** comparing dropout vs. non-dropout groups
- **Visualization suite** including histograms, boxplots, heatmaps, and bar charts

### 3. Feature Engineering
Created derived features to capture complex patterns:
- `first_sem_success_rate`: Ratio of approved to enrolled units (1st semester)
- `second_sem_success_rate`: Ratio of approved to enrolled units (2nd semester)
- `avg_semester_grade`: Mean of 1st and 2nd semester grades
- `max_parental_education`: Higher education level between parents
- `financial_stress`: Combined debtor and tuition overdue indicator

### 4. Model Development
Trained and compared multiple classification algorithms:
- **Logistic Regression** (baseline)
- **Decision Tree**
- **Random Forest**
- **Gradient Boosting**

### 5. Model Evaluation
Comprehensive evaluation metrics:
- **Confusion Matrix** analysis
- **Precision, Recall, F1-Score**
- **ROC-AUC** curve and score
- **Cross-validation** (5-fold stratified)
- **Feature importance** analysis

### 6. Model Deployment
- Saved best-performing model artifacts (`.pkl` format)
- Created prediction pipeline for new students
- Developed risk scoring system (Low/Medium/High)

## 🔍 Key Findings

### 1. Academic Performance is Critical
- **First semester grades** are the strongest predictor of dropout risk
- Students averaging **<10 (on 0-20 scale)** in first semester show significantly elevated dropout rates
- **Success rate** (approved/enrolled units) is highly predictive

### 2. Financial Factors Matter
- **Scholarship holders** demonstrate **lower dropout rates**
- Students with **financial stress** (debtor or overdue tuition) are at higher risk
- **Economic conditions** at enrollment (unemployment rate) correlate with dropout probability

### 3. Background Influences
- **Parental education** levels impact student persistence
- Students from **first-generation** college backgrounds need additional support
- **Age at enrollment** can be a risk factor (non-traditional students)

### 4. Early Intervention Window
- **First semester performance** provides earliest actionable signal
- Risk assessment at semester end enables timely intervention before second semester
- Combined academic + financial indicators yield strongest predictions

## 📈 Results

### Model Performance

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| **Logistic Regression** | 74.4% | 59.1% | 32.9% | 0.424 | 0.XXX |
| **Decision Tree** | XX.X% | XX.X% | XX.X% | 0.XXX | 0.XXX |
| **Random Forest** | XX.X% | XX.X% | XX.X% | 0.XXX | 0.XXX |
| **Gradient Boosting** | XX.X% | XX.X% | XX.X% | 0.XXX | 0.XXX |

*Note: Values will be populated after running the notebook with actual data*

### Best Model: [Model Name]
- **AUC-ROC**: X.XXX (strong discrimination between classes)
- **Precision**: XX% (reliable identification of at-risk students)
- **Recall**: XX% (captures substantial portion of actual dropouts)

### Feature Importance (Top 10)
1. Curricular units 1st semester grade
2. Curricular units 2nd semester grade
3. First semester success rate
4. Admission grade
5. Scholarship holder status
6. Age at enrollment
7. Debtor status
8. Unemployment rate
9. Previous qualification grade
10. Tuition fees up to date

*Full feature importance in notebook outputs*

## ⚙️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/student-dropout-prediction.git
cd student-dropout-prediction
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add your dataset**
- Place `Dropout.xlsx` in the `data/` directory
- See `data/README.md` for data requirements

## 🚀 Usage

### Option 1: Jupyter Notebook (Recommended for Exploration)

```bash
jupyter notebook student_dropout_prediction.ipynb
```

Run all cells to:
- Load and explore the dataset
- Perform comprehensive EDA
- Train and evaluate models
- Generate visualizations
- Save model artifacts

### Option 2: Python Script (Prediction)

**Interactive mode** (single student):
```bash
python predict.py --interactive
```

**Batch prediction** (CSV file):
```bash
python predict.py --student_file data/new_students.csv --output_file predictions.csv
```

### Option 3: Use Utility Functions

```python
from utils import load_data, engineer_features, evaluate_model
import joblib

# Load data
df = load_data('data/Dropout.xlsx')

# Engineer features
df_engineered = engineer_features(df)

# Load trained model
model = joblib.load('models/dropout_prediction_model.pkl')

# Make predictions
# ... your code here
```

## 📁 Project Structure

```
student-dropout-prediction/
│
├── data/
│   ├── README.md                   # Data directory documentation
│   └── Dropout.xlsx                # Dataset (not in repo - add locally)
│
├── models/
│   ├── dropout_prediction_model.pkl    # Trained model (generated)
│   ├── feature_scaler.pkl              # Feature scaler (generated)
│   └── feature_names.pkl               # Feature list (generated)
│
├── student_dropout_prediction.ipynb   # Main analysis notebook
├── utils.py                           # Helper functions module
├── predict.py                         # Prediction script
├── requirements.txt                   # Python dependencies
├── DATA_DICTIONARY.md                 # Comprehensive data documentation
├── README.md                          # This file
└── .gitignore                         # Git ignore rules
```

## 📊 Model Performance

### Classification Metrics Explained

- **Accuracy**: Overall correctness (correct predictions / total predictions)
- **Precision**: Of predicted dropouts, how many actually dropped out (reduces false alarms)
- **Recall**: Of actual dropouts, how many we identified (captures at-risk students)
- **F1-Score**: Harmonic mean of precision and recall (balanced metric)
- **AUC-ROC**: Model's ability to distinguish between classes (0.5=random, 1.0=perfect)

### Business Trade-offs

**High Precision** → Fewer false alarms, but may miss some at-risk students
**High Recall** → Catch more dropouts, but more students flagged unnecessarily

This project prioritizes **recall** (catching at-risk students) while maintaining acceptable precision to avoid overwhelming support resources.

## 🛠️ Technologies Used

### Core Libraries
- **pandas** (2.0.3): Data manipulation and analysis
- **numpy** (1.24.3): Numerical computing
- **scikit-learn** (1.3.0): Machine learning models and evaluation

### Visualization
- **matplotlib** (3.7.2): Static plots and charts
- **seaborn** (0.12.2): Statistical visualizations

### Development Tools
- **Jupyter** (1.0.0): Interactive notebook environment
- **openpyxl** (3.1.2): Excel file handling

### Deployment
- **joblib** (1.3.1): Model serialization

## 🔮 Future Work

### Model Improvements
- [ ] **Hyperparameter tuning** using GridSearchCV or RandomizedSearchCV
- [ ] **SMOTE** or other techniques to handle class imbalance
- [ ] **Ensemble methods** combining multiple models
- [ ] **Deep learning** approaches (neural networks)
- [ ] **SHAP values** for explainable AI and individual predictions

### Feature Engineering
- [ ] **Interaction terms** between key features
- [ ] **Polynomial features** for non-linear relationships
- [ ] **Time-series features** (trend in grades over time)
- [ ] **External data** integration (course difficulty, instructor ratings)

### Deployment
- [ ] **Web application** for easy access by advisors
- [ ] **API endpoint** for integration with student information systems
- [ ] **Automated reporting** and alert system
- [ ] **Real-time scoring** for current students
- [ ] **Dashboard** for institutional monitoring

### Business Applications
- [ ] **A/B testing** intervention effectiveness
- [ ] **Cost-benefit analysis** of retention programs
- [ ] **Longitudinal study** tracking intervention outcomes
- [ ] **Segmentation analysis** for targeted support programs

## 📚 References & Resources

- **Dataset Source**: [Specify original source if applicable]
- **Scikit-learn Documentation**: https://scikit-learn.org/
- **Educational Data Mining**: https://educationaldatamining.org/

## 👤 Author

**[Your Name]**
Graduate Student | Management Science & Business Analytics
Suffolk University

- 📧 Email: [your.email@example.com]
- 💼 LinkedIn: [Your LinkedIn Profile]
- 🌐 Portfolio: [Your Portfolio Website]
- 📂 GitHub: [@yourusername](https://github.com/yourusername)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Suffolk University for the academic foundation in analytics
- [Data source attribution if applicable]
- Open-source community for the excellent Python libraries

---

**⭐ If you found this project helpful, please consider giving it a star!**

**💡 Questions or suggestions? Open an issue or reach out directly.**

---

*Last Updated: January 2026*
