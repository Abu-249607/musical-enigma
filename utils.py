"""
Utility functions for Student Dropout Prediction project.

This module contains reusable functions for data preprocessing,
feature engineering, visualization, and model evaluation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_curve, roc_auc_score
)


def load_data(filepath='data/Dropout.xlsx'):
    """
    Load student dataset from Excel file.

    Parameters:
    -----------
    filepath : str
        Path to the Excel file

    Returns:
    --------
    pd.DataFrame
        Raw student data
    """
    df = pd.read_excel(filepath)
    print(f"Dataset loaded successfully")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.shape[1]}")
    print(f"Rows: {df.shape[0]}")
    return df


def clean_column_names(df):
    """
    Standardize column names to snake_case and remove special characters.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe

    Returns:
    --------
    pd.DataFrame
        DataFrame with cleaned column names
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace(r'[^a-z0-9_]', '', regex=True)
        .str.replace('__', '_')
        .str.replace('daytimeevening_attendance', 'attendance_type')
    )
    return df


def create_binary_target(df, target_col='target'):
    """
    Create binary dropout target variable.

    Dropout = 1 (at risk)
    Graduate or Enrolled = 0 (not at risk)

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    target_col : str
        Name of target column

    Returns:
    --------
    pd.DataFrame
        DataFrame with binary target
    """
    df = df.copy()
    df['dropout'] = (df[target_col] == 'Dropout').astype(int)
    return df


def identify_feature_types(df):
    """
    Categorize features into numerical and categorical.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe

    Returns:
    --------
    tuple
        (numerical_features, categorical_features)
    """
    exclude_cols = ['target', 'dropout']

    numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()
    numerical_features = [col for col in numerical_features if col not in exclude_cols]

    categorical_features = df.select_dtypes(include=['object']).columns.tolist()
    categorical_features = [col for col in categorical_features if col not in exclude_cols]

    return numerical_features, categorical_features


def detect_outliers_iqr(df, columns, threshold=3):
    """
    Detect outliers using IQR method.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    columns : list
        Columns to check for outliers
    threshold : float
        Number of IQRs beyond Q1/Q3 to consider outlier

    Returns:
    --------
    dict
        Outlier statistics for each column
    """
    outlier_stats = {}

    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR

        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        outlier_pct = (outliers / len(df)) * 100

        outlier_stats[col] = {
            'count': outliers,
            'percentage': round(outlier_pct, 2),
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }

    return outlier_stats


def remove_outliers(df, outlier_stats):
    """
    Remove outliers based on IQR bounds.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    outlier_stats : dict
        Outlier statistics from detect_outliers_iqr

    Returns:
    --------
    pd.DataFrame
        DataFrame with outliers removed
    """
    df_clean = df.copy()

    for col, stats in outlier_stats.items():
        df_clean = df_clean[
            (df_clean[col] >= stats['lower_bound']) &
            (df_clean[col] <= stats['upper_bound'])
        ]

    return df_clean


def engineer_features(df):
    """
    Create new features from existing data.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe

    Returns:
    --------
    pd.DataFrame
        DataFrame with engineered features
    """
    df = df.copy()

    # Academic performance features
    if 'curricular_units_1st_sem_approved' in df.columns and 'curricular_units_1st_sem_enrolled' in df.columns:
        df['first_sem_success_rate'] = np.where(
            df['curricular_units_1st_sem_enrolled'] > 0,
            df['curricular_units_1st_sem_approved'] / df['curricular_units_1st_sem_enrolled'],
            0
        )

    if 'curricular_units_2nd_sem_approved' in df.columns and 'curricular_units_2nd_sem_enrolled' in df.columns:
        df['second_sem_success_rate'] = np.where(
            df['curricular_units_2nd_sem_enrolled'] > 0,
            df['curricular_units_2nd_sem_approved'] / df['curricular_units_2nd_sem_enrolled'],
            0
        )

    # Average semester grades
    if 'curricular_units_1st_sem_grade' in df.columns and 'curricular_units_2nd_sem_grade' in df.columns:
        df['avg_semester_grade'] = (df['curricular_units_1st_sem_grade'] + df['curricular_units_2nd_sem_grade']) / 2

    # Parental education level (max of mother and father)
    if 'mothers_qualification' in df.columns and 'fathers_qualification' in df.columns:
        df['max_parental_education'] = df[['mothers_qualification', 'fathers_qualification']].max(axis=1)

    # Economic stress indicator
    if 'debtor' in df.columns and 'tuition_fees_up_to_date' in df.columns:
        df['financial_stress'] = ((df['debtor'] == 1) | (df['tuition_fees_up_to_date'] == 0)).astype(int)

    return df


def prepare_features_for_modeling(df, target_col='dropout'):
    """
    Prepare features for modeling: handle encoding and select relevant features.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    target_col : str
        Target column name

    Returns:
    --------
    tuple
        (X, y, feature_names, scaler_features)
    """
    df = df.copy()

    # Drop original target and any ID columns
    drop_cols = [target_col, 'target'] + [col for col in df.columns if 'id' in col.lower()]
    drop_cols = [col for col in drop_cols if col in df.columns]

    X = df.drop(columns=drop_cols)
    y = df[target_col]

    # Identify features to scale (continuous numerical features)
    scale_features = [
        col for col in X.columns if col in [
            'age_at_enrollment', 'admission_grade', 'previous_qualification_grade',
            'curricular_units_1st_sem_grade', 'curricular_units_2nd_sem_grade',
            'unemployment_rate', 'inflation_rate', 'gdp',
            'avg_semester_grade', 'first_sem_success_rate', 'second_sem_success_rate'
        ]
    ]

    return X, y, X.columns.tolist(), scale_features


def plot_target_distribution(df, target_col='dropout'):
    """
    Visualize the distribution of the target variable.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    target_col : str
        Name of target column
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Count plot
    dropout_counts = df[target_col].value_counts()
    colors = ['#2ecc71', '#e74c3c']
    axes[0].bar(['No Dropout', 'Dropout'], dropout_counts.values, color=colors)
    axes[0].set_ylabel('Count')
    axes[0].set_title('Dropout Distribution (Count)', fontsize=12, fontweight='bold')
    for i, v in enumerate(dropout_counts.values):
        axes[0].text(i, v + 50, str(v), ha='center', fontweight='bold')

    # Percentage plot
    dropout_pct = df[target_col].value_counts(normalize=True) * 100
    axes[1].bar(['No Dropout', 'Dropout'], dropout_pct.values, color=colors)
    axes[1].set_ylabel('Percentage (%)')
    axes[1].set_title('Dropout Distribution (Percentage)', fontsize=12, fontweight='bold')
    for i, v in enumerate(dropout_pct.values):
        axes[1].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')

    plt.tight_layout()
    plt.show()


def plot_correlation_heatmap(df, features):
    """
    Plot correlation heatmap for numerical features.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    features : list
        List of features to include in heatmap
    """
    correlation_matrix = df[features].corr()

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={'shrink': 0.8}
    )
    plt.title('Correlation Matrix - Numerical Features', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()


def evaluate_model(y_true, y_pred, y_pred_proba, model_name='Model'):
    """
    Comprehensive model evaluation.

    Parameters:
    -----------
    y_true : array-like
        True labels
    y_pred : array-like
        Predicted labels
    y_pred_proba : array-like
        Predicted probabilities
    model_name : str
        Name of the model
    """
    print(f"\n{'='*60}")
    print(f"{model_name} - Evaluation Results")
    print(f"{'='*60}\n")

    # Classification report
    print("Classification Report:")
    print(classification_report(y_true, y_pred, target_names=['No Dropout', 'Dropout']))

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)

    # Calculate metrics
    tn, fp, fn, tp = cm.ravel()

    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\nKey Metrics:")
    print(f"  Accuracy:    {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision:   {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall:      {recall:.4f} ({recall*100:.2f}%)")
    print(f"  Specificity: {specificity:.4f} ({specificity*100:.2f}%)")
    print(f"  F1-Score:    {f1:.4f}")

    # AUC-ROC
    if y_pred_proba is not None:
        auc_score = roc_auc_score(y_true, y_pred_proba)
        print(f"  AUC-ROC:     {auc_score:.4f}")

    # Confusion Matrix Visualization
    plt.figure(figsize=(8, 6))
    cm_df = pd.DataFrame(
        cm,
        index=['Actual: No Dropout', 'Actual: Dropout'],
        columns=['Predicted: No Dropout', 'Predicted: Dropout']
    )
    sns.heatmap(cm_df, annot=True, fmt='d', cmap='Blues', cbar=False, square=True, linewidths=2)
    plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold', pad=20)
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.show()


def plot_roc_curve(y_true, y_pred_proba, model_name='Model'):
    """
    Plot ROC curve.

    Parameters:
    -----------
    y_true : array-like
        True labels
    y_pred_proba : array-like
        Predicted probabilities
    model_name : str
        Name of the model
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    auc_score = roc_auc_score(y_true, y_pred_proba)

    plt.figure(figsize=(10, 6))
    plt.plot(fpr, tpr, color='#e74c3c', linewidth=2, label=f'{model_name} (AUC = {auc_score:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', linewidth=2, linestyle='--', label='Random Classifier (AUC = 0.500)')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve - Dropout Prediction', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_feature_importance_logreg(model, feature_names, top_n=20):
    """
    Plot feature importance from logistic regression coefficients.

    Parameters:
    -----------
    model : LogisticRegression
        Trained logistic regression model
    feature_names : list
        List of feature names
    top_n : int
        Number of top features to plot
    """
    # Get coefficients
    coefficients = model.coef_[0]

    # Create dataframe
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'coefficient': coefficients,
        'abs_coefficient': np.abs(coefficients)
    }).sort_values('abs_coefficient', ascending=False)

    # Plot top N features
    top_features = feature_importance.head(top_n)

    plt.figure(figsize=(10, 8))
    colors = ['#e74c3c' if x > 0 else '#2ecc71' for x in top_features['coefficient']]
    plt.barh(range(len(top_features)), top_features['coefficient'], color=colors)
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Coefficient Value', fontsize=12)
    plt.title(f'Top {top_n} Most Important Features (Logistic Regression)', fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Print odds ratios for top features
    print("\nTop Features - Odds Ratios:")
    print("="*60)
    for idx, row in top_features.head(10).iterrows():
        odds_ratio = np.exp(row['coefficient'])
        direction = "increases" if row['coefficient'] > 0 else "decreases"
        print(f"{row['feature']:40s} OR: {odds_ratio:.3f} ({direction} dropout risk)")
