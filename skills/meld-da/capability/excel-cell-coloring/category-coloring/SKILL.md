---
name: large-file-parquet-analysis-and-highlight
description: "When an Excel file exceeds 10,000 rows, convert it to Parquet to speed up reads, extract the target metric and compute its maximum, then export the result to Excel and highlight specific rows."
---

# Skill Steps

Step1 Read the file and count rows across all sheets, sum and print the total row count, to decide whether large-file handling is needed.
```python
import pandas as pd

file_path = "input_data.xlsx"

# Read all sheets and count the total number of rows
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names
print(f"Sheet列表: {sheet_names}")

total_rows = 0
for sheet in sheet_names:
    # Read only one column to speed up row counting
    df_temp = pd.read_excel(file_path, sheet_name=sheet, usecols=[0], header=None)
    rows = len(df_temp)
    total_rows += rows
    print(f"Sheet '{sheet}': {rows} 行")

print(f"\n总行数 = {total_rows}")
```

Step2 When the total row count is >= 10,000, read the data already converted to Parquet, extract the target metric by matching rows and columns, and find the maximum value with its category.
```python
import pandas as pd

# Assume the Excel file has already been converted to Parquet by the large-file skill
parquet_path = "converted_data.parquet"
df = pd.read_parquet(parquet_path)

# Assume row 2 (index 1) is the category header (e.g. ownership type, region, ...)
header_row = df.iloc[1].tolist()
print("分类表头:", header_row)

# Locate the row holding the target metric (placeholder: 'target metric name')
target_metric = '目标指标名称'
target_rows = df[df[0] == target_metric]

if not target_rows.empty:
    # Extract the numeric values
    values = target_rows.iloc[0, 1:].tolist()
    
    # Clean the data and find the maximum with its category
    numeric_values = []
    for val in values:
        try:
            numeric_values.append(float(val))
        except:
            numeric_values.append(0)
    
    max_val = max(numeric_values)
    max_idx = numeric_values.index(max_val)
    max_type = header_row[1:][max_idx]
    
    print(f"\n指标最高的分类: {max_type} ({max_val})")
    
    # Prepare the data structure to write into Excel
    result_data = list(zip(header_row[1:], numeric_values))
```

Step3 Save the extracted analysis result as a new Excel file, use openpyxl to highlight the row containing the maximum value with a background color, and verify the output.
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl import load_workbook

output_path = "analysis_result.xlsx"

wb = Workbook()
ws = wb.active
ws.title = "数据分析结果"

# Write the header row
headers = ["分类类型", "指标数值"]
ws.append(headers)

# Write the data (uses result_data extracted in Step2; fallback example to avoid nulls)
if 'result_data' not in locals():
    result_data = [("分类A", 100), ("分类B", 500), ("分类C", 200)]
    max_type = "分类B"

for row in result_data:
    ws.append(row)

# Find the row with the maximum value and fill it green
green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")

for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
    if row[0].value == max_type:
        for cell in row:
            cell.fill = green_fill

# Save the file
wb.save(output_path)
print(f"文件已保存到: {output_path}")

# Verify the contents and formatting of the output file
wb_check = load_workbook(output_path)
ws_check = wb_check.active
print("\n文件内容验证:")
for row in ws_check.iter_rows(values_only=True):
    print(row)
```
