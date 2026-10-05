---
name: formatted-export-with-parquet
description: "Identify records matching specified conditions in a multi-sheet Excel file and export the filtered result as an Excel file with whole rows highlighted red, suited to data cleaning, condition filtering and visual marking."
---

# Formatted_Export

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

## Skill Steps

Step1 Scan all sheets, locate the target column via fuzzy matching, and filter records matching the condition (e.g. nulls or invalid characters).
```python
empty_target_rows = []
for sheet_name, sheet_df in all_sheets.items():
    target_col = None
    
    # Prefer matching the target column name (example: a column containing a specific keyword)
    for col in sheet_df.columns:
        if 'keyword1' in str(col).lower() or 'keyword2' in str(col).lower():
            target_col = col
            break
            
    if target_col is None:
        # Try the secondary inference logic
        for col in sheet_df.columns:
            if 'keyword3' in str(col) and ('keyword4' in str(col)):
                target_col = col
                break
                
    if target_col is None:
        continue
    
    # Data cleaning: filter rows with nulls and invalid characters (e.g. spaces, 'nan')
    mask = sheet_df[target_col].isna() | (sheet_df[target_col].astype(str).str.strip() == '') | (sheet_df[target_col].astype(str).str.strip() == 'nan')
    empty_rows = sheet_df[mask].copy()
    
    if len(empty_rows) > 0:
        empty_rows.insert(0, '来源Sheet', sheet_name)
        empty_target_rows.append(empty_rows)

# Merge the results
result_df = pd.concat(empty_target_rows, ignore_index=True) if empty_target_rows else pd.DataFrame()
```

Step2 Export the filtered records as an Excel file with whole rows highlighted red for visual identification, and report the output path.
```python
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

output_path = "filtered_results_highlighted.xlsx"

if not result_df.empty:
    # Export the base data
    result_df.to_excel(output_path, index=False)

    # Load the workbook for formatting
    wb = load_workbook(output_path)
    ws = wb.active
    
    # Define the red fill style
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

    # Walk all data rows and fill them red (skip the header)
    for row in range(2, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            ws.cell(row=row, column=col).fill = red_fill

    wb.save(output_path)
    print(f"结果文件已保存: {output_path}")
    print(f"下载链接: [点击下载标红结果文件]({output_path})")
else:
    print("未找到符合条件的记录，无需导出。")
```
