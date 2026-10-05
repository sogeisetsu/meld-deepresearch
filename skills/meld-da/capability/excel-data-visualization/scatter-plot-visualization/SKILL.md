---
name: excel-statistical-viz-large-file
description: "Run multi-dimensional statistical analysis and visualization on Excel data."
---

# excel_statistical_visualization

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Data cleaning and standardization. Extract the target analysis columns, handle merged cells (ffill), and clean numeric fields with regex or type conversion to keep the analysis dataset accurate.
```python
import re

# Assume target_col_x and target_col_y are the analysis targets
# Handle missing values caused by merged cells
df['group_col'] = df['group_col'].fillna(method='ffill')

def clean_numeric_string(value):
    if pd.isna(value): return None
    # Keep digits, decimal point and minus sign; drop spaces and illegal characters
    cleaned = re.sub(r'[^\d\.\-]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return None

df['x_val'] = df['target_col_x'].apply(clean_numeric_string)
df['y_val'] = df['target_col_y'].apply(clean_numeric_string)

# Filter out invalid data
df_clean = df.dropna(subset=['x_val', 'y_val']).copy()
```

Step2 Run multi-dimensional statistical analysis. Compute category shares, mean and standard deviation, and build a cross-analysis table (crosstab/pivot) to back the visualization.
```python
# Category statistics and shares
stats_summary = df_clean.groupby('group_col')['y_val'].agg(['count', 'mean', 'std', 'min', 'max'])
stats_summary['percentage'] = (stats_summary['count'] / stats_summary['count'].sum()) * 100

# Add a total row
total_row = pd.DataFrame(df_clean[['y_val']].agg(['count', 'mean']).T)
total_row.index = ['Total']

# Cross analysis example
pivot_table = pd.pivot_table(df_clean, values='y_val', index='group_col', columns='category_col', aggfunc='count', fill_value=0)
```

Step3 Generate high-resolution visualizations: scatter plot, linear trend line (R^2, p-value), box plot or bar chart combinations, with Chinese fonts and polish parameters configured.
```python
import matplotlib.pyplot as plt
import matplotlib
from scipy import stats
import numpy as np

# Font configuration: prefer SimHei or DejaVu Sans so Chinese text renders correctly
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

x = df_clean['x_val'].values
y = df_clean['y_val'].values

# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
line = slope * x + intercept

plt.figure(figsize=(12, 8), dpi=300)

# Scatter plot: add random jitter to avoid overlapping points
jitter_x = x + np.random.normal(0, 0.01, size=len(x))
plt.scatter(jitter_x, y, alpha=0.6, edgecolors='w', label='Data Points')

# Trend line
plt.plot(x, line, color='red', linestyle='--', linewidth=2, 
         label=f'Trend: y={slope:.4f}x+{intercept:.4f}\n$R^2$={r_value**2:.4f}, p={p_value:.4e}')

# Data point annotation (practical tip: annotate only extremes or specific points)
for i, (xi, yi) in enumerate(zip(x, y)):
    if i % (len(x)//5 or 1) == 0: # Sampled annotation to avoid crowding
        plt.annotate(f'({xi:.2f}, {yi:.2f})', (xi, yi), textcoords="offset points", xytext=(5,5), fontsize=8)

plt.xlabel('Dimension X')
plt.ylabel('Dimension Y')
plt.title('Statistical Distribution & Trend Analysis')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

output_img = 'analysis_plot.png'
plt.savefig(output_img, bbox_inches='tight')
plt.show()
```

Step4 Export the analysis results. Save the cleaned data and statistics summary as CSV or Excel files.
```python
output_csv = 'cleaned_analysis_data.csv'
# utf-8-sig keeps Chinese text readable when Excel opens the CSV
df_clean.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Visualization saved to: {output_img}")
print(f"Data exported to: {output_csv}")
# Print the key regression metrics for quick reference
print(f"R-squared: {r_value**2:.6f}, P-value: {p_value:.6f}")
```
