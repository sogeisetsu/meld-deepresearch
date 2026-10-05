---
name: multi-sheet-reading-and-analysis
description: "Read a multi-worksheet Excel file, evaluate the data volume dynamically to enable Parquet large-file optimization, and run regex cleaning, category summarization, linear fitting, plus formatted charts and result files."
---

Step1 Count the total rows across worksheets and enable Parquet conversion dynamically by data volume (e.g. >= 10,000 rows) to optimize large-file read performance.
```python
import pandas as pd
import os
import tempfile
from openpyxl import load_workbook

file_path = "your_excel_file.xlsx"
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names

# Count data rows across all sheets
total_rows = 0
for sheet in sheet_names:
    wb = load_workbook(file_path, read_only=True, data_only=True)
    ws = wb[sheet]
    max_row = ws.max_row
    data_rows = max_row - 1 if max_row > 0 else 0
    total_rows += data_rows
    wb.close()

print(f"总数据行数: {total_rows}")

# Large-file optimization: convert to Parquet for reading
if total_rows >= 10000:
    df = pd.read_excel(file_path, sheet_name=sheet_names[0])
    parquet_path = os.path.join(tempfile.gettempdir(), 'temp_data.parquet')
    df.to_parquet(parquet_path, engine='pyarrow')
    df = pd.read_parquet(parquet_path)
else:
    df = pd.read_excel(file_path, sheet_name=sheet_names[0])
```

Step2 Clean a specified text column with a regular expression (e.g. keep only CJK characters).
```python
import re

def clean_chinese_text(text):
    if pd.isna(text):
        return text
    s = str(text)
    # Extract all CJK characters
    chinese_chars = re.findall(r'[一-鿿]', s)
    cleaned = ''.join(chinese_chars)
    return cleaned if cleaned != '' else ''

target_col = '目标清洗列' # Replace with your actual column name
if target_col in df.columns:
    df[target_col] = df[target_col].apply(clean_chinese_text)
```

Step3 Extract key data for multi-dimensional analysis (category summary with extrema, or bivariate linear fitting).
```python
import numpy as np

# Mode 1: category summary and extremum extraction
group_col = '分类列'
value_col = '数值列'
# Example placeholder data extraction logic
summary = pd.DataFrame({
    group_col: ['类别A', '类别B', '类别C'],
    value_col: [100, 500, 200]
})
max_idx = summary[value_col].idxmax()
max_type = summary.loc[max_idx, group_col]

# Mode 2: bivariate linear relationship analysis
x_col = 'X轴列'
y_col = 'Y轴列'
if x_col in df.columns and y_col in df.columns:
    x_data = df[x_col].values
    y_data = df[y_col].values
    # Fit a linear trend line
    coefficients = np.polyfit(x_data, y_data, 1)
    trend_line = np.poly1d(coefficients)(x_data)
```

Step4 Generate an Excel report with conditional formatting (e.g. highlighting the maximum) and visualization charts, and report their output paths.
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
import matplotlib.pyplot as plt

# 1. Generate the Excel file with style markers
wb = Workbook()
ws = wb.active
ws.title = "分析结果"

# Style definitions
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(name="SimHei", bold=True, color="FFFFFF", size=12)
highlight_fill = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
highlight_font = Font(name="SimHei", bold=True, color="FFFFFF", size=12)
normal_font = Font(name="SimHei", size=11)
center_align = Alignment(horizontal="center", vertical="center")
thin_border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))

# Write the header and data
headers = [group_col, value_col]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_align
    cell.border = thin_border

for row_idx, row in summary.iterrows():
    c_type = ws.cell(row=row_idx+2, column=1, value=row[group_col])
    c_val = ws.cell(row=row_idx+2, column=2, value=row[value_col])
    for cell in [c_type, c_val]:
        cell.alignment = center_align
        cell.border = thin_border
        cell.font = normal_font
    # Highlight the maximum-value row
    if row[group_col] == max_type:
        c_type.fill = highlight_fill
        c_type.font = highlight_font
        c_val.fill = highlight_fill
        c_val.font = highlight_font

output_excel_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), "analysis_report.xlsx")
wb.save(output_excel_path)

# 2. Generate the scatter plot and trend line (if fit data exists)
if 'x_data' in locals():
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(10, 6), dpi=100)
    plt.scatter(x_data, y_data, color='blue', s=80, label='数据点')
    plt.plot(x_data, trend_line, color='red', linewidth=2, label=f'趋势线: y={coefficients[0]:.2f}x+{coefficients[1]:.2f}')
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f'{x_col} vs {y_col} 散点图与趋势线')
    plt.legend()
    plt.grid(True)
    output_img_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), 'scatter_plot.png')
    plt.savefig(output_img_path, bbox_inches='tight')
    plt.close()

print(f"文件已生成，下载链接:")
print(f"- 分析报告: {output_excel_path}")
if 'x_data' in locals():
    print(f"- 趋势图表: {output_img_path}")
```
