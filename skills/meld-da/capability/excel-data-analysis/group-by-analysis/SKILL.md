---
name: group-by-analysis
description: "Count rows of a multi-sheet Excel file, preprocess it with large-file Parquet conversion, clean the data and run a group-by aggregation, producing a styled statistics table and visualization charts."
---

Step1 Clean and preprocess the data, including handling merged cells, regex filtering and category mapping.
```python
import re

# 1. Handle merged cells: forward fill
target_col = 'category_column'
df[target_col] = df[target_col].ffill()

# 2. Regex cleaning: strip invalid characters or filter a specific format
def clean_text(text):
    if pd.isna(text): return text
    return re.sub(r'[^\w\s]', '', str(text)).strip()

df[target_col] = df[target_col].apply(clean_text)

# 3. Category mapping function skeleton
def map_categories(value):
    mapping = {
        'example_key_1': 'Group_A',
        'example_key_2': 'Group_B'
    }
    return mapping.get(value, 'Others')

df['group_tag'] = df[target_col].apply(map_categories)
```

Step2 Run the grouped statistics: compute counts and shares, and add a total row.
```python
group_col = 'group_tag'
value_col = 'value_column'

# Group aggregation: count and sum
summary = df.groupby(group_col)[value_col].agg(['count', 'sum']).reset_index()

# Compute the share
total_sum = summary['sum'].sum()
summary['percentage'] = (summary['sum'] / total_sum).map(lambda x: f"{x:.2%}")

# Add the total row
total_row = pd.DataFrame({
    group_col: ['Total'],
    'count': [summary['count'].sum()],
    'sum': [total_sum],
    'percentage': ['100.00%']
})
summary_final = pd.concat([summary, total_row], ignore_index=True)

print(summary_final)
```

Step3 Generate a bar chart with Chinese font support, value labels and a polished grid.
```python
import matplotlib.pyplot as plt

# Enable Chinese font support
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

plt.figure(figsize=(10, 6), dpi=100)
bars = plt.bar(summary[group_col], summary['sum'], color='#4472C4')

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:,.0f}', ha='center', va='bottom', fontsize=10)

plt.title("Distribution Analysis", fontsize=14)
plt.xlabel(group_col)
plt.ylabel("Values")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

chart_path = "analysis_chart.png"
plt.savefig(chart_path)
```

Step4 Use openpyxl to produce an Excel report with styles and conditional formatting, then report the output path.
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

output_path = "analysis_report.xlsx"
wb = Workbook()
ws = wb.active
ws.title = "Summary Report"

# Define the styles
header_style = {
    "fill": PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid"),
    "font": Font(bold=True, color="FFFFFF"),
    "alignment": Alignment(horizontal="center"),
    "border": Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))
}

highlight_style = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")

# Write the data and apply styles
for r_idx, row in enumerate(summary_final.values, 2):
    for c_idx, value in enumerate(row, 1):
        cell = ws.cell(row=r_idx, column=c_idx, value=value)
        # Example: mark the row containing the maximum value in green
        if value == summary['sum'].max():
            cell.fill = highlight_style

# Auto-adjust column widths
for col in ws.columns:
    max_length = max(len(str(cell.value)) for cell in col)
    ws.column_dimensions[col[0].column_letter].width = max_length + 2

wb.save(output_path)
print(f"Download link: {output_path}")
```
