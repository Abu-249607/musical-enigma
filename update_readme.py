"""
Update README with Actual Results

This script reads the analysis results and updates the README.md file
with actual performance metrics and visualizations.

Usage:
    python update_readme.py

Requirements:
    - Run run_analysis.py first to generate results
    - results/analysis_summary.json must exist

Author: [Your Name]
"""

import json
import os
import re

def load_results():
    """Load analysis results from JSON file."""
    if not os.path.exists('results/analysis_summary.json'):
        print("❌ Error: results/analysis_summary.json not found")
        print("\nPlease run the analysis first:")
        print("  python run_analysis.py")
        return None

    with open('results/analysis_summary.json', 'r') as f:
        return json.load(f)

def update_readme_with_results(results):
    """Update README.md with actual results."""

    # Read current README
    with open('README.md', 'r') as f:
        readme = f.read()

    # Extract data
    best_model = results['best_model']
    dataset = results['dataset']
    all_models = results['all_models']

    # Update dataset size
    readme = re.sub(
        r'- \*\*Size\*\*: \d+,?\d* student records',
        f"- **Size**: {dataset['total_records']:,} student records",
        readme
    )

    # Update class distribution
    readme = re.sub(
        r'- \*\*Dropout\*\*: ~\d+% \(\d+,?\d* students\)',
        f"- **Dropout**: {dataset['dropout_percentage']:.1f}% ({dataset['dropout_count']:,} students)",
        readme
    )

    # Update model performance table
    model_table = "| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |\n"
    model_table += "|-------|----------|-----------|--------|----------|---------|\\n"

    for model_name in all_models['Accuracy'].keys():
        accuracy = all_models['Accuracy'][model_name]
        precision = all_models['Precision'][model_name]
        recall = all_models['Recall'][model_name]
        f1 = all_models['F1-Score'][model_name]
        auc = all_models['AUC-ROC'][model_name]

        star = "**" if model_name == best_model['name'] else ""
        model_table += f"| {star}{model_name}{star} | {accuracy*100:.1f}% | {precision*100:.1f}% | {recall*100:.1f}% | {f1:.3f} | {auc:.3f} |\n"

    # Replace the placeholder table
    table_pattern = r'\| Model \| Accuracy \| Precision.*?\n\*Note: Values will be populated.*?\n'
    readme = re.sub(
        table_pattern,
        model_table + "\n",
        readme,
        flags=re.DOTALL
    )

    # Update best model section
    best_model_section = f"""### Best Model: {best_model['name']}
- **AUC-ROC**: {best_model['auc_roc']:.3f} (strong discrimination between classes)
- **Precision**: {best_model['precision']*100:.1f}% (reliable identification of at-risk students)
- **Recall**: {best_model['recall']*100:.1f}% (captures substantial portion of actual dropouts)
- **Accuracy**: {best_model['accuracy']*100:.1f}%"""

    # Replace placeholder
    readme = re.sub(
        r'### Best Model: \[Model Name\].*?- \*\*Recall\*\*:.*?\n',
        best_model_section + "\n",
        readme,
        flags=re.DOTALL
    )

    # Add visualization links section if not present
    viz_section = """

## 📸 Sample Visualizations

### Confusion Matrix
![Confusion Matrix](visualizations/04_confusion_matrix.png)

### ROC Curve
![ROC Curve](visualizations/05_roc_curve.png)

### Feature Importance
![Feature Importance](visualizations/07_feature_importance.png)

### Model Comparison
![Model Comparison](visualizations/06_model_comparison.png)

*More visualizations available in the `visualizations/` directory*
"""

    # Insert visualizations section before "Installation" if not already present
    if "## 📸 Sample Visualizations" not in readme:
        readme = readme.replace(
            "## ⚙️ Installation",
            viz_section + "\n## ⚙️ Installation"
        )

    # Save updated README
    with open('README.md', 'w') as f:
        f.write(readme)

    print("✅ README.md updated successfully!")
    print("\nUpdated sections:")
    print(f"  • Dataset size: {dataset['total_records']:,} records")
    print(f"  • Best model: {best_model['name']}")
    print(f"  • AUC-ROC: {best_model['auc_roc']:.3f}")
    print(f"  • Accuracy: {best_model['accuracy']*100:.1f}%")
    print(f"  • Model comparison table updated")
    print(f"  • Visualization links added")

def main():
    print("="*60)
    print("README UPDATE SCRIPT")
    print("="*60)

    # Load results
    print("\nLoading analysis results...")
    results = load_results()

    if results is None:
        return

    print("✓ Results loaded")

    # Update README
    print("\nUpdating README.md...")
    update_readme_with_results(results)

    print("\n" + "="*60)
    print("README UPDATE COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the updated README.md")
    print("2. Add your personal information (name, email, LinkedIn)")
    print("3. Commit the changes: git add README.md && git commit -m 'Update README with results'")
    print("4. Push to GitHub: git push")

if __name__ == '__main__':
    main()
