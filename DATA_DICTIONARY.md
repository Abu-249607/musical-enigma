# Data Dictionary - Student Dropout Dataset

## Overview

This dataset contains information about student enrollment, academic performance, demographics, and outcomes for higher education students. The primary objective is to predict student dropout risk.

## Target Variable

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| **Target** | Categorical | 'Dropout', 'Graduate', 'Enrolled' | Student's current academic status |
| **dropout** (derived) | Binary | 0, 1 | Binary target (1 = Dropout, 0 = Graduate or Enrolled) |

## Demographic Features

| Variable | Type | Range/Values | Description |
|----------|------|--------------|-------------|
| **Marital status** | Categorical | 1-6 | 1=Single, 2=Married, 3=Widowed, 4=Divorced, 5=Facto union, 6=Legally separated |
| **Age at enrollment** | Numerical | 17-70+ | Student's age when enrolling in the program |
| **Gender** | Binary | 0, 1 | 0=Female, 1=Male |
| **Nacionality** | Categorical | 1-109 | Student's nationality (coded) |
| **International** | Binary | 0, 1 | 0=Domestic student, 1=International student |

## Academic Background

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| **Application mode** | Categorical | 1-57 | Method of application to the institution |
| **Application order** | Numerical | 0-9 | Order of this course in student's application preferences |
| **Course** | Categorical | Various | Enrolled course/program identifier |
| **Daytime/evening attendance** | Binary | 0, 1 | 0=Evening, 1=Daytime attendance |
| **Previous qualification** | Categorical | 1-43 | Type of previous education qualification |
| **Previous qualification (grade)** | Numerical | 95-190 | Final grade from previous qualification (0-200 scale) |
| **Admission grade** | Numerical | 95-190 | Grade/score for admission to the course (0-200 scale) |

## Family Background

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| **Mother's qualification** | Categorical | 1-44 | Mother's highest education level (1=None to 44=Doctorate) |
| **Father's qualification** | Categorical | 1-44 | Father's highest education level (1=None to 44=Doctorate) |
| **Mother's occupation** | Categorical | 0-195 | Mother's occupation (coded by occupation type) |
| **Father's occupation** | Categorical | 0-195 | Father's occupation (coded by occupation type) |

## Financial/Administrative Status

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| **Scholarship holder** | Binary | 0, 1 | 0=No scholarship, 1=Scholarship recipient |
| **Debtor** | Binary | 0, 1 | 0=Not a debtor, 1=Has outstanding debts |
| **Tuition fees up to date** | Binary | 0, 1 | 0=Fees overdue, 1=Fees current |
| **Displaced** | Binary | 0, 1 | 0=Not displaced, 1=Displaced student |
| **Educational special needs** | Binary | 0, 1 | 0=No special needs, 1=Has special educational needs |

## First Semester Academic Performance

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| **Curricular units 1st sem (credited)** | Numerical | 0-20 | Number of units credited in 1st semester |
| **Curricular units 1st sem (enrolled)** | Numerical | 0-26 | Number of units enrolled in 1st semester |
| **Curricular units 1st sem (evaluations)** | Numerical | 0-45 | Number of evaluations in 1st semester |
| **Curricular units 1st sem (approved)** | Numerical | 0-26 | Number of units approved in 1st semester |
| **Curricular units 1st sem (grade)** | Numerical | 0-18.88 | Average grade in 1st semester (0-20 scale) |
| **Curricular units 1st sem (without evaluations)** | Numerical | 0-12 | Number of units without evaluations in 1st semester |

## Second Semester Academic Performance

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| **Curricular units 2nd sem (credited)** | Numerical | 0-19 | Number of units credited in 2nd semester |
| **Curricular units 2nd sem (enrolled)** | Numerical | 0-23 | Number of units enrolled in 2nd semester |
| **Curricular units 2nd sem (evaluations)** | Numerical | 0-33 | Number of evaluations in 2nd semester |
| **Curricular units 2nd sem (approved)** | Numerical | 0-20 | Number of units approved in 2nd semester |
| **Curricular units 2nd sem (grade)** | Numerical | 0-18.57 | Average grade in 2nd semester (0-20 scale) |
| **Curricular units 2nd sem (without evaluations)** | Numerical | 0-12 | Number of units without evaluations in 2nd semester |

## Macroeconomic Indicators

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| **Unemployment rate** | Numerical | 7.6-16.2 | National unemployment rate at time of enrollment (%) |
| **Inflation rate** | Numerical | -3.7 to 3.7 | National inflation rate at time of enrollment (%) |
| **GDP** | Numerical | -4.06 to 3.51 | GDP growth rate at time of enrollment (%) |

## Engineered Features (Created During Analysis)

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| **first_sem_success_rate** | Numerical | 0-1 | Ratio of approved to enrolled units in 1st semester |
| **second_sem_success_rate** | Numerical | 0-1 | Ratio of approved to enrolled units in 2nd semester |
| **avg_semester_grade** | Numerical | 0-20 | Average of 1st and 2nd semester grades |
| **max_parental_education** | Numerical | 1-44 | Higher education level between mother and father |
| **financial_stress** | Binary | 0, 1 | 1 if debtor OR tuition fees overdue, 0 otherwise |

## Data Quality Notes

### Missing Values
- The original dataset has no missing values
- All features are complete for all students

### Data Types
- Binary features: Coded as 0 and 1
- Categorical features: Integer codes representing categories
- Numerical features: Continuous or discrete numerical values

### Scales and Units

**Portuguese Grading Scale (0-20)**
- Used for: Semester grades, previous qualification grade, admission grade
- 0-9: Fail
- 10-13: Sufficient
- 14-15: Good
- 16-17: Very Good
- 18-20: Excellent

**Success Rate**
- Scale: 0.0 to 1.0
- 1.0 = 100% of enrolled units approved
- 0.0 = 0% of enrolled units approved

**Economic Indicators**
- Unemployment rate: Percentage (e.g., 10.8 = 10.8%)
- Inflation rate: Percentage (can be negative for deflation)
- GDP: Growth rate percentage (can be negative for contraction)

## Data Sources

- **Academic data**: Institutional student information system
- **Economic indicators**: National statistical office data
- **Time period**: [Specify years covered]
- **Geography**: [Specify country/region]

## Data Privacy

This dataset has been anonymized:
- Student names and IDs removed
- Categorical codes used instead of identifying information
- Aggregated/coded family and background information

## Usage Recommendations

### For Modeling:
1. **Scale numerical features** with different ranges (admission grade, GDP, etc.)
2. **Handle high-cardinality categoricals** (Course, Nationality, Parent occupations) via encoding
3. **Consider class imbalance** between dropout and non-dropout students
4. **Feature engineer** success rates and combined metrics for better predictive power
5. **Use stratified sampling** to maintain target distribution in train/test splits

### For Interpretation:
1. **First semester grades** are the strongest early indicator
2. **Financial factors** (scholarship, debtor, tuition status) matter significantly
3. **Parental education** influences outcomes
4. **Economic conditions** at enrollment time have measurable impact

---

**Last Updated**: [Date]
**Version**: 1.0
**Contact**: [Your contact information]
