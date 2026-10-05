---
name: numeric-extraction-and-distribution-analysis
description: "Extract numbers from unit-suffixed string columns and clean them, producing a combined distribution panel of histogram, pie, bar and cumulative-distribution charts that show central tendency and distribution shape."
---

# Numeric_Extraction_and_Distribution_Analysis

## Skill Steps

Step1 Extract the target columns from the raw data, drop invalid and empty values, and safely convert unit-suffixed strings to numeric type
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configure Chinese/English fonts to avoid garbled chart text
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

item_col = '项目名称'  # Placeholder example: the category or name column
value_col = '带单位的数值'  # Placeholder example: the raw column to extract numbers from
numeric_col = '提取数值'
unit_str = 'g'  # Placeholder example: the unit string to remove

def extract_numeric_value(val_str):
    """Extract a number from a unit-suffixed string"""
    if pd.isna(val_str):
        return None
    try:
        # Remove the unit and convert to float
        return float(str(val_str).replace(unit_str, '').strip())
    except ValueError:
        return None

# Drop missing values and anomalous placeholders
df_clean = df.dropna(subset=[item_col, value_col]).copy()
df_clean = df_clean[df_clean[item_col] != '...']

# Apply the extraction function and drop rows that failed to convert
df_clean[numeric_col] = df_clean[value_col].apply(extract_numeric_value)
df_clean = df_clean.dropna(subset=[numeric_col])
```

Step2 Create a base distribution histogram and add mean and median reference lines to show central tendency
```python
plt.figure(figsize=(12, 8))

# Draw the histogram
plt.hist(df_clean[numeric_col], bins=10, alpha=0.7, color='skyblue', edgecolor='black')

# Compute and add mean/median reference lines
mean_val = df_clean[numeric_col].mean()
median_val = df_clean[numeric_col].median()
plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'平均值: {mean_val:.2f}')
plt.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'中位数: {median_val:.2f}')

plt.xlabel(f'{numeric_col}', fontsize=12)
plt.ylabel('频数', fontsize=12)
plt.title(f'{numeric_col}分布直方图', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

Step3 Generate a combined panel of histogram, pie, bar and cumulative-distribution charts to fully show the numeric distribution, and save a high-resolution image
```python
# Create a 2x2 subplot layout
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Histogram
ax1.hist(df_clean[numeric_col], bins=8, alpha=0.7, color='lightblue', edgecolor='black', rwidth=0.8)
ax1.set_xlabel(f'{numeric_col}', fontsize=12)
ax1.set_ylabel('频数', fontsize=12)
ax1.set_title(f'{numeric_col}分布直方图', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 2. Pie chart (shares based on value_counts)
val_counts = df_clean[numeric_col].value_counts().sort_index()
colors = plt.cm.Set3(np.linspace(0, 1, len(val_counts)))
ax2.pie(val_counts.values, labels=[f'{x}' for x in val_counts.index], autopct='%1.1f%%', colors=colors, startangle=90)
ax2.set_title(f'{numeric_col}占比分布', fontsize=14, fontweight='bold')

# 3. Bar chart
val_counts.plot(kind='bar', ax=ax3, color='lightcoral', alpha=0.8)
ax3.set_xlabel(f'{numeric_col}', fontsize=12)
ax3.set_ylabel('数量', fontsize=12)
ax3.set_title(f'各{numeric_col}对应的数量', fontsize=14, fontweight='bold')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3)

# 4. Cumulative distribution plot
sorted_values = np.sort(df_clean[numeric_col])
cumulative_freq = np.arange(1, len(sorted_values) + 1) / len(sorted_values) * 100
ax4.plot(sorted_values, cumulative_freq, marker='o', linewidth=2, markersize=6, color='darkgreen')
ax4.set_xlabel(f'{numeric_col}', fontsize=12)
ax4.set_ylabel('累积百分比 (%)', fontsize=12)
ax4.set_title(f'{numeric_col}累积分布', fontsize=14, fontweight='bold')
ax4.grid(True, alpha=0.3)

# Adjust layout and save
plt.tight_layout()
output_path = 'distribution_dashboard.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
```
