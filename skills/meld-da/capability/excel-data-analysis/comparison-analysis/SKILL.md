---
name: categorical-comparison-analysis
description: "Compare two groups of categorical data, count differences and ratios, and produce visualization charts."
---

# categorical-comparison-analysis

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Read the file and count the total rows of all sheets to decide whether large-file optimization is needed.
```python
import pandas as pd
from pandas import read_excel
from pathlib import Path

# Count rows across all sheets to choose a processing strategy
file_path = "input_data.xlsx"
sheet_names = pd.ExcelFile(file_path).sheet_names
total_rows = 0
for sheet in sheet_names:
    # Read only the row index column for a fast count
    df_tmp = read_excel(file_path, sheet_name=sheet, usecols=[0])
    total_rows += len(df_tmp)

print(f"Total rows across all sheets: {total_rows}")
```

Step2 Extract the category information of the comparison dimensions and clean the data, including dropping nulls, forward-filling merged cells, and excluding non-data rows.
```python
# Define the target column names
target_col_a = "category_a_column"
target_col_b = "category_b_column"

# Handle merged cells (ffill) and clean the data
df[target_col_a] = df[target_col_a].ffill()
df[target_col_b] = df[target_col_b].ffill()

# Exclude header-row placeholders (e.g. '代码', '名称') and nulls
exclude_val = "代码" 
data_a = df[target_col_a].dropna()
data_a = data_a[data_a != exclude_val]

data_b = df[target_col_b].dropna()
data_b = data_b[data_b != exclude_val]
```

Step3 Count the categories, compute the difference and share, and build a multi-dimensional comparison statistics table.
```python
count_a = len(data_a)
count_b = len(data_b)
total_count = count_a + count_b
difference = abs(count_a - count_b)

# Compute the shares
ratio_a = (count_a / total_count) * 100 if total_count > 0 else 0
ratio_b = (count_b / total_count) * 100 if total_count > 0 else 0

# Build the statistics summary
summary_df = pd.DataFrame({
    "分类名称": ["类别A", "类别B"],
    "数量": [count_a, count_b],
    "占比": [f"{ratio_a:.2f}%", f"{ratio_b:.2f}%"]
})
print(summary_df)
print(f"数量差异: {difference}")
```

Step4 Configure a Chinese font and generate the visualization charts (bar and pie) with polished output.
```python
import matplotlib.pyplot as plt

# Chinese font configuration
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
labels = ['类别A', '类别B']
counts = [count_a, count_b]
colors = ['#3498db', '#e74c3c']

# Polish the bar chart
bars = ax1.bar(labels, counts, color=colors, alpha=0.8, edgecolor='black')
ax1.set_title('分类数量对比', fontsize=14)
ax1.grid(axis='y', linestyle='--', alpha=0.6)
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{int(height)}', 
             ha='center', va='bottom', fontweight='bold')

# Polish the pie chart
ax2.pie(counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, explode=(0.05, 0))
ax2.set_title('分类比例分布', fontsize=14)

output_img = "comparison_analysis_chart.png"
plt.tight_layout()
plt.savefig(output_img, dpi=300, bbox_inches='tight')
plt.show()
```

Step5 Export the analysis result as an Excel file and provide a link to it.
```python
from IPython.display import FileLink

output_path = "analysis_report.xlsx"
with pd.ExcelWriter(output_path) as writer:
    summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
    # Detailed rows can also be exported here if available

print(f"分析报告已生成")
display(FileLink(output_path, result_html_prefix="下载分析报告: "))
```
