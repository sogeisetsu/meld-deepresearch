---
name: excel-outlier-detection-and-highlighting
description: "Identify out-of-limit values and erroneous cells in an Excel file and highlight them."
---

# Outlier_Coloring

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Extract limit values with regular expressions and, combined with context logic, identify rows whose overall heat transfer coefficient exceeds the limit.
```python
import re

exceed_rows = []
target_col = 0  # Assume the feature column is the first column
value_col = 8   # Assume the value column is the ninth column

for i, row in df.iterrows():
    row_str = str(row.iloc[target_col]) if pd.notna(row.iloc[target_col]) else ""
    
    # Precisely extract the limit value with regex, e.g. "限值0.5"
    if '限值' in row_str:
        match = re.search(r'限值([\d.]+)', row_str)
        if match:
            current_limit = float(match.group(1))
            
    # Identify calculation-result rows and compare
    if '共计' in row_str:
        try:
            actual_val = float(row.iloc[value_col])
            # Trace backwards to find the structure name (practical trick: walk rows to restore context)
            structure_name = "未知结构"
            for j in range(i-1, max(0, i-15), -1):
                prev_val = str(df.iloc[j, 0])
                if any(kw in prev_val for kw in ['系数', '围护']):
                    structure_name = prev_val
                    break
            
            # Extract the most recent limit value for comparison
            limit_val = None
            for j in range(i-1, max(0, i-15), -1):
                check_str = ' '.join([str(x) for x in df.iloc[j, :] if pd.notna(x)])
                limit_match = re.search(r'限值([\d.]+)', check_str)
                if limit_match:
                    limit_val = float(limit_match.group(1))
                    break
            
            if limit_val and actual_val > limit_val:
                exceed_rows.append({
                    'row_index': i,
                    'name': structure_name,
                    'value': actual_val,
                    'limit': limit_val,
                    'diff': actual_val - limit_val
                })
        except (ValueError, TypeError):
            continue
```

Step2 Walk the specified sheet to find cells containing errors such as '#DIV/' and record their coordinates.
```python
# Detect formula errors on a specific sheet (e.g. Sheet3)
ws_error = wb['Sheet3']
error_cells = []

for row in ws_error.iter_rows(min_row=1, max_row=ws_error.max_row):
    for cell in row:
        if cell.value is not None:
            val_str = str(cell.value)
            # Detect Excel division-by-zero errors or other anomaly markers
            if '#DIV/' in val_str:
                error_cells.append({
                    'coord': cell.coordinate,
                    'val': cell.value
                })
```

Step3 Highlight the identified over-limit rows and erroneous cells in red, then save the result.
```python
from openpyxl.styles import PatternFill

# Define the red fill style
red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

# Mark over-limit rows (note: Excel row number = pandas index + 1)
# Assume marking on the first sheet
ws_main = wb[wb.sheetnames[0]]
for item in exceed_rows:
    excel_row = item['row_index'] + 1
    for col in range(1, ws_main.max_column + 1):
        ws_main.cell(row=excel_row, column=col).fill = red_fill

# Mark erroneous cells
for err in error_cells:
    ws_error[err['coord']].fill = red_fill

output_path = "highlighted_report.xlsx"
wb.save(output_path)
```

Step4 Summarize the over-limit data into an analysis report and provide the output path.
```python
# Build the summary DataFrame
summary_df = pd.DataFrame(exceed_rows)
if not summary_df.empty:
    summary_df['Excel行号'] = summary_df['row_index'] + 1
    summary_df = summary_df[['Excel行号', 'name', 'value', 'limit', 'diff']]
    summary_df.columns = ['行号', '结构名称', '实测值', '限值', '超出值']

summary_path = "outlier_summary.xlsx"
summary_df.to_excel(summary_path, index=False)

# Print the plain output paths
print(f"处理完成。结果文件：{output_path}")
print(f"汇总报告：{summary_path}")
```
