---
name: excel-multi-sheet-dynamic-analysis
description: "Analyze a multi-sheet Excel file, judging the data volume dynamically to decide whether to convert to Parquet for large-file handling, with cross-sheet field statistics, data cleaning, cross analysis and visualization, finally producing a summary report with its output path."
---

Step1 Walk all sheets, locate target columns flexibly, and count fields of a specific type.
```python
target_col_keyword = 'type' # Placeholder example
target_val_keyword = 'varchar' # Placeholder example

total_target_count = 0
target_details = []

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    raw_data = list(ws.iter_rows(values_only=True))

    # Practical tip: flexible strategy to locate the target column - scan the first few rows to find the header row
    header_row_idx = None
    for i, row in enumerate(raw_data):
        if any(cell and isinstance(cell, str) and target_col_keyword in str(cell).lower() for cell in row):
            header_row_idx = i
            break

    if header_row_idx is not None:
        header = raw_data[header_row_idx]
        type_col_idx = next((j for j, col in enumerate(header) if col and target_col_keyword in str(col).lower()), None)
        
        if type_col_idx is not None:
            target_count = 0
            target_fields = []
            for i in range(header_row_idx + 1, len(raw_data)):
                row = raw_data[i]
                if len(row) <= type_col_idx:
                    continue
                cell_val = row[type_col_idx]
                if cell_val and isinstance(cell_val, str) and target_val_keyword in cell_val.lower():
                    target_count += 1
                    field_name = row[0] if len(row) > 0 else None
                    if field_name and field_name not in target_fields:
                        target_fields.append(field_name)
                        
            total_target_count += target_count
            target_details.append({
                'sheet': sheet_name,
                'target_count': target_count,
                'target_fields': target_fields[:10]
            })
```

Step2 Clean data, map categories, score multi-dimensionally, and run cross-aggregation analysis for a specific sheet.
```python
import pandas as pd
import re

# Read the specific sheet and handle the column names
sheet1_df = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl', header=None, skiprows=1)
sheet1_df.columns = ['id_col', 'name_col', 'year_col', 'value_col', 'group_col'] # Placeholder example

# Merged-cell handling (ffill + walk to restore)
sheet1_df['group_col'] = sheet1_df['group_col'].ffill()

# Data cleaning regex (extract numbers)
sheet1_df['value_col'] = sheet1_df['value_col'].astype(str).str.replace(r'[^\d.]', '', regex=True)
sheet1_df['value_col'] = pd.to_numeric(sheet1_df['value_col'], errors='coerce').fillna(0)

# Category mapping function skeleton (concrete values replaced with placeholders; structure kept)
def map_category(val):
    if pd.isna(val): return 'Unknown'
    if 'keyword' in str(val): return 'Category A' # Placeholder example
    return 'Other'
sheet1_df['mapped_category'] = sheet1_df['name_col'].apply(map_category)

# Multi-dimensional scoring/grading algorithm structure
def calculate_score(row):
    score = 0
    if row['value_col'] > 100: score += 50 # Placeholder example
    if row['mapped_category'] == 'Category A': score += 50
    return score
sheet1_df['score'] = sheet1_df.apply(calculate_score, axis=1)

# Filter records matching a specific condition
target_val = 'target_value' # Placeholder example
filtered_df = sheet1_df[sheet1_df['group_col'] == target_val]
count = len(filtered_df)
total_value = filtered_df['value_col'].sum()

# value_counts + share + total row
stats_df = sheet1_df['group_col'].value_counts().rename('数量').to_frame()
stats_df['占比'] = sheet1_df['group_col'].value_counts(normalize=True).apply(lambda x: f"{x:.2%}")
stats_df.loc['总计'] = [stats_df['数量'].sum(), '100.00%']

# Cross analysis crosstab/pivot
cross_table = pd.crosstab(sheet1_df['group_col'], sheet1_df['mapped_category'], margins=True, margins_name='总计')

result_df = pd.DataFrame({
    '统计项': [f'{target_val} 数量', f'{target_val} 总值'],
    '数值': [count, total_value]
})
```

Step3 Visualize and polish the statistical results.
```python
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Chinese/English font configuration (SimHei, DejaVu Sans)
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Chart polish (dpi, color scheme, label positions)
plt.figure(figsize=(10, 6), dpi=120)
plot_data = stats_df.drop('总计') # Exclude the total row when plotting
ax = sns.barplot(x=plot_data.index, y=plot_data['数量'], palette='Blues_d')

# Optimize label positions
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='bottom', fontsize=10)

plt.title('各分组数量统计')
plt.xlabel('分组')
plt.ylabel('数量')
plt.tight_layout()

plot_path = os.path.join(os.getcwd(), 'stats_chart.png')
plt.savefig(plot_path)
plt.close()
```

Step4 Save all analysis results as an Excel file and provide a clickable output link.
```python
from datetime import datetime
from IPython.display import HTML, display
import os

summary_df = pd.DataFrame([{'total_target_count': total_target_count}])
details_df = pd.DataFrame(target_details)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"analysis_result_{timestamp}.xlsx"
output_path = os.path.join(os.getcwd(), output_filename)

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='汇总表', index=False)
    details_df.to_excel(writer, sheet_name='详细列表', index=False)
    result_df.to_excel(writer, sheet_name='特定条件统计', index=False)
    stats_df.to_excel(writer, sheet_name='分组统计')
    cross_table.to_excel(writer, sheet_name='交叉分析')

print(f"\n文件已保存至: {output_path}")

# Output link generation
download_link = f'<a href="{output_path}" download="{output_path}">点击下载分析结果</a>'
display(HTML(download_link))
```
