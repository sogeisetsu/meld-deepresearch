---
name: stacked-chart-visualization
description: "Handle category share data containing percentage strings, fill in missing dimensions and generate stacked bar charts that show how the multi-dimensional composition changes over time or across categories."
---

# Stacked_Chart_Visualization

Step1 Define a percentage conversion function and extract the raw data. Convert percentage formats to computable floats via regex or string handling.
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure a Chinese font so chart labels render correctly
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def convert_percentage(val):
    """
    Convert a percentage string to a float.
    Logic: strip the percent sign and convert to float; return the value directly if already numeric.
    """
    if isinstance(val, str):
        return float(val.strip('%'))
    return val

# Example data extraction logic (replace with DataFrame extraction in real use)
time_labels = ['1月', '2月', '3月', '4月', '5月', '6月'] # Generalized time axis
cat1_raw = ['23.21%', '22.98%', '24.31%', '24.53%', '23.84%', '24.80%']
cat2_raw = ['25.17%', '25.67%', '25.77%', '25.98%', '25.17%', '25.61%']
cat3_raw = ['28.12%', '28.37%', '26.58%', '25.83%', '26.49%', '25.17%']

cat1_ratios = [convert_percentage(x) for x in cat1_raw]
cat2_ratios = [convert_percentage(x) for x in cat2_raw]
cat3_ratios = [convert_percentage(x) for x in cat3_raw]
```

Step2 Build a structured data table, integrating the cleaned values into a DataFrame for vectorized computation.
```python
# Build the structured table with the time dimension and each category's share
df = pd.DataFrame({
    'group_col': time_labels,
    'cat_1': cat1_ratios,
    'cat_2': cat2_ratios,
    'cat_3': cat3_ratios
})
```

Step3 Compute the shares of missing dimensions. With some dimensions' shares known, derive the remaining dimensions from the constraint that the total is 100%, and validate the data.
```python
# Compute the total share of the known dimensions
target_cols = ['cat_1', 'cat_2', 'cat_3']
df['current_total'] = df[target_cols].sum(axis=1)

# Derive the remaining dimension's share (e.g. 'other' or a specific category)
df['cat_remainder'] = 100 - df['current_total']

# Validate data integrity: all dimensions together should approach 100
df['final_check'] = df[target_cols + ['cat_remainder']].sum(axis=1)
```

Step4 Visualize with a stacked bar chart. The core is the `bottom` parameter accumulating heights layer by layer, plus polished chart aesthetics.
```python
# Set the plotting style and canvas
plt.figure(figsize=(12, 6), dpi=100)
sns.set_style('whitegrid')

# Core stacking logic: each layer's bottom is the sum of the heights of previous layers
plt.bar(df['group_col'], df['cat_1'], label='分类1', color='#5DADE2')
plt.bar(df['group_col'], df['cat_2'], bottom=df['cat_1'], label='分类2', color='#58D68D')
plt.bar(df['group_col'], df['cat_3'], bottom=df['cat_1'] + df['cat_2'], label='分类3', color='#EC7063')
plt.bar(df['group_col'], df['cat_remainder'], bottom=df['cat_1'] + df['cat_2'] + df['cat_3'], label='其他', color='#F4D03F')

# Polish the chart's auxiliary elements
plt.xlabel('统计周期')
plt.ylabel('占比 (%)')
plt.title('多维度占比变化趋势分析')
plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1))
plt.xticks(rotation=45) # Avoid overlapping labels
plt.tight_layout()
```

Step5 Export the analysis result. Save the generated chart as a high-resolution image and free memory.
```python
# Save the chart; dpi keeps it sharp and bbox_inches prevents labels from being clipped
output_path = 'stacked_ratio_analysis.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
plt.close()
```
