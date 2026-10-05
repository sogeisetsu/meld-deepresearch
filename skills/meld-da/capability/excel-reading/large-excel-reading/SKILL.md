---
name: large-excel-analysis-and-formatting
description: "Process large multi-sheet Excel files with optional Parquet conversion for speed, and use openpyxl to generate a formatted Excel report with conditional highlighting, custom styles and its output path."
---

## Skill Steps

Step1 Read the Excel file and count the total rows of all sheets. If the data volume is large (e.g. >= 10,000 rows), convert it to Parquet to significantly speed up subsequent reads and analysis.
```python
import pandas as pd
import os
import tempfile

file_path = "input.xlsx"
xls = pd.ExcelFile(file_path)
total_rows = 0

# Count the total rows across all sheets
for name in xls.sheet_names:
    df_temp = pd.read_excel(file_path, sheet_name=name, header=None)
    total_rows += len(df_temp)

print(f"总行数: {total_rows}")

# Large-file handling: convert to Parquet above the threshold for efficiency
if total_rows >= 10000:
    parquet_path = os.path.join(tempfile.gettempdir(), "temp.parquet")
    # Here we read the first sheet as an example; merge multiple sheets as needed
    df = pd.read_excel(file_path, sheet_name=0)
    df.to_parquet(engine='pyarrow', path=parquet_path)
    df = pd.read_parquet(parquet_path)
else:
    df = pd.read_excel(file_path, sheet_name=0)
```

Step2 Extract the target data for a grouped summary analysis, and identify the maximum value with its corresponding category.
```python
# Placeholder example: replace the column names with your dataset's
group_col = '分类列名'  # e.g. '控股类型'
target_col = '目标数值列'  # e.g. '建筑业总产值'

# Assume df is cleaned and contains the required columns; run the summary analysis
summary = df.groupby(group_col)[target_col].sum().reset_index()

# Identify the maximum value and its category
max_idx = summary[target_col].idxmax()
max_type = summary.loc[max_idx, group_col]
print(f"最高产值类型: {max_type}")
```

Step3 Use openpyxl to write the analysis result into a new Excel file, configure header styles, borders and column widths, highlight rows meeting a specific condition (e.g. the maximum) in green, and finally report the output path.
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

wb = Workbook()
ws = wb.active
ws.title = "分析报告"

# Style definitions
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(name="微软雅黑", bold=True, color="FFFFFF", size=12)
highlight_fill = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
highlight_font = Font(name="微软雅黑", bold=True, color="FFFFFF", size=12)
normal_font = Font(name="微软雅黑", size=11)
center_align = Alignment(horizontal="center", vertical="center")
thin_border = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin")
)

# Write the header and apply styles
headers = [group_col, target_col]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_align
    cell.border = thin_border

# Write the data and apply conditional highlighting
for row_idx, row_data in enumerate(summary.itertuples(index=False), 2):
    type_name, value = row_data[0], row_data[1]
    
    cell_type = ws.cell(row=row_idx, column=1, value=type_name)
    cell_value = ws.cell(row=row_idx, column=2, value=value)
    
    # Base styles
    for cell in [cell_type, cell_value]:
        cell.alignment = center_align
        cell.border = thin_border
        cell.font = normal_font
    
    # Highlight the whole row when the maximum-value condition hits
    if type_name == max_type:
        cell_type.fill = highlight_fill
        cell_type.font = highlight_font
        cell_value.fill = highlight_fill
        cell_value.font = highlight_font

# Adjust the column widths
ws.column_dimensions['A'].width = 18
ws.column_dimensions['B'].width = 25

# Save the file next to the user's data (or in the run's output directory)
output_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), "formatted_analysis_report.xlsx")
wb.save(output_path)
print(f"文件已保存至: {output_path}")

# Report the plain output path
download_link = output_path
print(f"下载链接: {download_link}")
```
