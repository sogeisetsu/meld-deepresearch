---
name: large-file-conditional-formatting
description: "Switch automatically to Parquet-accelerated reads based on the total row count of the Excel file, compute time-series averages for a given dimension, and use openpyxl to produce an analysis report with conditional formatting (e.g. below-average rows in green) and custom styles."
---

## Skill Steps

> **Note**: This sub-skill covers one step of the Excel analysis workflow. For the full pipeline (file reading, row counting, large-file optimization, export), see the parent workflow SKILL.md.


Step1 Read the file and count rows across all sheets, sum and print the total, to decide whether large-file acceleration is needed.
```python
import pandas as pd
import openpyxl

file_path = "input_data.xlsx"

# Get all sheet names
wb = openpyxl.load_workbook(file_path, read_only=True)
sheet_names = wb.sheetnames
print("Sheet列表:", sheet_names)
print("Sheet数量:", len(sheet_names))

# Count rows in each sheet
total_rows = 0
for name in sheet_names:
    df_temp = pd.read_excel(file_path, sheet_name=name, header=None)
    rows = len(df_temp)
    total_rows += rows
    print(f"Sheet '{name}': {rows} 行")

print(f"\n总行数 = {total_rows}")
```

Step2 Extract the time-series data for the target entity, compute the average, and build a structured DataFrame containing the comparison results.
```python
target_entity = 'Target_Entity' # Placeholder example, e.g. 'US'

# Extract the target row (assume column 0 holds entity names)
target_row = df[df[0] == target_entity]

# Extract time labels and matching values (assume row 6 is the header, columns 1:10 are data)
time_labels = df.iloc[6, 1:10].tolist()
target_values = target_row.iloc[0, 1:10].tolist()
target_values_numeric = [float(v) for v in target_values]

# Compute the average
avg_value = sum(target_values_numeric) / len(target_values_numeric)

# Build the result DataFrame
result_data = {
    '时间维度': time_labels,
    '指标数值': target_values_numeric,
    '是否低于平均值': [v < avg_value for v in target_values_numeric]
}
result_df = pd.DataFrame(result_data)
```

Step3 Use openpyxl to save the analysis result as an Excel file, apply fine-grained styling (bold title, borders, centered alignment), and conditionally fill rows below the average (in green).
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

wb = Workbook()
ws = wb.active
ws.title = "指标分析报告"

# Define the styles
green_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF")
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

# Set the main title
ws.merge_cells('A1:D1')
ws['A1'] = f"目标实体指标分析 - 平均值: {avg_value:.2f}"
ws['A1'].font = Font(bold=True, size=14)
ws['A1'].alignment = Alignment(horizontal='center')

# Set the header row
headers = ['时间维度', '指标数值', '与平均值比较', '是否标绿']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=3, column=col, value=header)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center')
    cell.border = thin_border

# Write the data and apply conditional formatting
for i, row_data in result_df.iterrows():
    row_num = i + 4
    time_label = row_data['时间维度']
    value = row_data['指标数值']
    below_avg = row_data['是否低于平均值']
    
    # Write each column's data
    ws.cell(row=row_num, column=1, value=time_label).alignment = Alignment(horizontal='center')
    ws.cell(row=row_num, column=2, value=value).alignment = Alignment(horizontal='center')
    
    diff = value - avg_value
    ws.cell(row=row_num, column=3, value=f"{diff:+.2f}").alignment = Alignment(horizontal='center')
    ws.cell(row=row_num, column=4, value="是" if below_avg else "否").alignment = Alignment(horizontal='center')
    
    # Add borders and fill the whole row green when the condition holds
    for col in range(1, 5):
        cell = ws.cell(row=row_num, column=col)
        cell.border = thin_border
        if below_avg:
            cell.fill = green_fill

# Adjust column widths
ws.column_dimensions['A'].width = 15
ws.column_dimensions['B'].width = 20
ws.column_dimensions['C'].width = 18
ws.column_dimensions['D'].width = 12

output_path = "output_report.xlsx"
wb.save(output_path)
print(f"分析报告已保存至: {output_path}")
```
