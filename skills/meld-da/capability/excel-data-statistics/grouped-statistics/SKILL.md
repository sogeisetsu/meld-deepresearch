---
name: grouped-statistics
description: "Row counting, data merging and forward fill for multi-sheet Excel files."
---

## Skill Steps

> **Note**: This sub-skill covers one step of the Excel analysis workflow. For the full pipeline (file reading, row counting, large-file optimization, export), see the parent workflow SKILL.md.

Step1 Extract key dimensions and metric information, handle merged-cell missing values, and run multi-table cross analysis with sorting.
```python
import pandas as pd

# Set the target column names
group_col = '行业名称'
target_val_1 = '企业单位数'
target_val_2 = '工业总产值'

# Read the first sheet and clean it
df1 = pd.read_excel(file_path, sheet_name=sheet_names[0], header=None)
# Assume the data starts at row 21; extract the dimension and value columns
data_1 = df1.iloc[21:63, [0, 2]].copy()
data_1.columns = [group_col, target_val_1]

# Handle merged cells: forward-fill the dimension column
data_1[group_col] = data_1[group_col].ffill()
data_1[target_val_1] = pd.to_numeric(data_1[target_val_1], errors='coerce')

# Read the second sheet and extract supplementary metrics
df2 = pd.read_excel(file_path, sheet_name=sheet_names[1], header=None)
data_2 = df2.iloc[5:47, [0, 1]].copy()
data_2.columns = ['temp_dim', target_val_2]
data_2[target_val_2] = pd.to_numeric(data_2[target_val_2], errors='coerce')

# Cross analysis: merge on the index or the dimension column
merged_df = pd.merge(data_1, data_2.reset_index(), left_index=True, right_index=True, how='inner')
merged_df = merged_df[[group_col, target_val_1, target_val_2]].dropna(subset=[target_val_1])

# Keep the Top N results
top5_df = merged_df.nlargest(5, target_val_1).reset_index(drop=True)
top5_df.index = top5_df.index + 1
print(top5_df)
```

Step2 Format and annotate the filtered key data (red marking, borders, alignment) to produce a polished Excel file.
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

output_path = 'analysis_report.xlsx'
wb = Workbook()
ws = wb.active
ws.title = 'Top_Analysis'

# Define the styles
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
header_font = Font(bold=True, color='FFFFFF', size=12)
red_font = Font(color='FF0000', bold=True)
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                    top=Side(style='thin'), bottom=Side(style='thin'))
center_align = Alignment(horizontal='center', vertical='center')

# Write the header row
headers = ['排名'] + list(top5_df.columns)
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border

# Write the data and apply conditional formatting
for idx, row in top5_df.iterrows():
    row_num = idx + 1 # Account for the header row
    # Rank column
    ws.cell(row=row_num, column=1, value=idx).border = thin_border
    # Dimension column
    ws.cell(row=row_num, column=2, value=row[group_col]).border = thin_border
    # Value column 1
    cell_v1 = ws.cell(row=row_num, column=3, value=row[target_val_1])
    cell_v1.border = thin_border
    cell_v1.number_format = '#,##0'
    # Value column 2 (marked red)
    cell_v2 = ws.cell(row=row_num, column=4, value=row[target_val_2])
    cell_v2.font = red_font
    cell_v2.border = thin_border
    cell_v2.number_format = '#,##0.00'

# Adjust the column widths
ws.column_dimensions['B'].width = 35
ws.column_dimensions['C'].width = 15
ws.column_dimensions['D'].width = 18

wb.save(output_path)
```

Step3 Output the final result and report its path.
```python
# Confirm the file was created and report its path
import os
if os.path.exists(output_path):
    print(f"分析完成。结果文件已生成，下载链接：{output_path}")
else:
    print("文件生成失败，请检查路径权限。")
```
