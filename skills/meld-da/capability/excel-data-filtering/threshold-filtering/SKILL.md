---
name: excel-threshold-analysis-and-styling
description: "Decide the processing strategy automatically from the Excel data volume, clean numeric columns, filter by condition, and use openpyxl to style matching cells and export."
---

# Excel Threshold Analysis and Styling

> **Note**: This sub-skill covers one step of the Excel analysis workflow. For the full pipeline (file reading, row counting, large-file optimization, export), see the parent workflow SKILL.md.


Step1 Read the row counts of all worksheets in the Excel file and total them to assess the data scale.
```python
import pandas as pd

file_path = 'input_file.xlsx'

# Read all sheet names and count the total rows
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names
total_rows = 0

for sheet in sheet_names:
    # header=None quickly counts total rows including the header
    df_tmp = pd.read_excel(file_path, sheet_name=sheet, header=None)
    rows = len(df_tmp)
    total_rows += rows
    print(f"Sheet '{sheet}': {rows} 行")

print(f"\n总行数汇总: {total_rows}")
```

Step2 Clean the target data sheet: convert non-numeric content of the specified column to missing values and drop them, ensuring the data type is numeric.
```python
target_sheet = 'Sheet1'
target_col = '数量' # Target column name to process
header_idx = 1     # Row index of the header (0-based)

df = pd.read_excel(file_path, sheet_name=target_sheet, header=header_idx)

# Force numeric conversion; content that cannot convert becomes NaN and is dropped
df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
df_cleaned = df.dropna(subset=[target_col])

print(f"清洗完成，有效数据行数: {len(df_cleaned)}")
```

Step3 Filter records matching a specific numeric condition and compute statistics.
```python
filter_threshold = 10 
df_filtered = df_cleaned[df_cleaned[target_col] > filter_threshold]

print(f"{target_col} 大于 {filter_threshold} 的记录共有 {len(df_filtered)} 条")
```

Step4 Use openpyxl on the original file to
