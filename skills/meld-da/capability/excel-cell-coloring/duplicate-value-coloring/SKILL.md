---
name: excel-conditional-comparison-and-large-file-processing
description: "Compare a specific coefficient across multiple sheets in an Excel workbook and color-mark the anomalous values."
---

# excel-conditional-comparison-and-large-file-processing

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Extract values of a specific dimension (e.g. "B1 layer") from different sheets and compare them across tables logically.
```python
# Extraction logic: locate the target row (e.g. a row containing 'B1') and get its associated coefficient
def extract_target_value(df, target_label='B1', label_col_idx=0, offset_row=1, value_col_idx=2):
    """
    Search for a label in the specified column and return the value
    at its relative offset position.
    """
    extracted_values = []
    for idx, row in df.iterrows():
        if str(row.iloc[label_col_idx]).strip() == target_label:
            # Extract the value below the target row or at a specific offset
            if idx + offset_row < len(df):
                val = df.iloc[idx + offset_row].iloc[value_col_idx]
                extracted_values.append(val)
    return extracted_values

# Read the sheets that need to be compared
sheet1_df = pd.read_excel(file_path, sheet_name='Sheet1')
sheet2_df = pd.read_excel(file_path, sheet_name='Sheet2')

# Extract the coefficients (example: conversion coefficients of the B1 layer)
# Note: column indexes may differ between sheets; adjust to your actual structure
s1_coeffs = extract_target_value(sheet1_df, target_label='B1', label_col_idx=1, value_col_idx=3)
s2_coeffs = extract_target_value(sheet2_df, target_label='B1', label_col_idx=0, value_col_idx=2)

# Gather the comparison data
comparison_results = []
target_standard = 0.6 # Preset standard threshold

for val in s1_coeffs:
    comparison_results.append({'source': 'Sheet1', 'value': val, 'is_anomaly': val != target_standard})
for val in s2_coeffs:
    comparison_results.append({'source': 'Sheet2', 'value': val, 'is_anomaly': val != target_standard})
```

Step2 Generate a comparison report and use openpyxl to mark anomalous values (non-standard coefficients) in red.
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill

output_path = 'comparison_report.xlsx'
wb = Workbook()
ws = wb.active
ws.title = "Comparison Analysis"

# Write the header row
headers = ['数据来源', '提取数值', '是否符合标准', '状态标记']
ws.append(headers)

# Define the red fill style
red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

# Walk the results and write them while applying conditional formatting
for item in comparison_results:
    status_text = '正常' if not item['is_anomaly'] else '异常(非0.6)'
    row_data = [item['source'], item['value'], '是' if not item['is_anomaly'] else '否', status_text]
    ws.append(row_data)
    
    # If it is an anomaly, fill the row (or specific cells) red
    if item['is_anomaly']:
        curr_row = ws.max_row
        for col_idx in range(1, len(headers) + 1):
            ws.cell(row=curr_row, column=col_idx).fill = red_fill

# Save the result and report its path
wb.save(output_path)
print(f"Analysis complete. Report saved to: {output_path}")
```
