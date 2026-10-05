---
name: excel-conditional-filtering-optimization
description: "Filter Excel data by multi-dimensional numeric conditions and export the results, with automatic performance optimization for large data."
---

# Excel_Conditional_Filtering_Optimization

> **Note**: This sub-skill covers one step of the Excel analysis workflow. For the full pipeline (file reading, row counting, large-file optimization, export), see the parent workflow SKILL.md.


Step1 Read all worksheets of the Excel file, count and total the rows of each sheet to assess the data scale.
```python
import pandas as pd

file_path = "input_data.xlsx"

# Read all sheets and count the rows
xls = pd.ExcelFile(file_path)
print("Sheet names:", xls.sheet_names)

total_rows = 0
sheet_details = []
for sheet in xls.sheet_names:
    df_temp = pd.read_excel(file_path, sheet_name=sheet)
    row_count = len(df_temp)
    sheet_details.append({"sheet": sheet, "rows": row_count})
    total_rows += row_count

print(f"Sheet details: {sheet_details}")
print(f"Total rows across all sheets: {total_rows}")
```

Step2 Clean the target data, handle header offsets, and convert key columns to numeric types to ensure accurate computation.
```python
# Read the target data sheet
target_sheet = 'Sheet1'
df = pd.read_excel(file_path, sheet_name=target_sheet, header=0)

# Handle possible sub-header or blank-row offsets (example: skip the first row)
# df = df.iloc[1:].reset_index(drop=True)

# Set uniform column names (adjust the placeholders to your business logic)
# df.columns = ['col_1', 'col_2', 'col_3', 'target_id', 'val_a', 'val_b', 'val_c']

# Force numeric conversion, turning non-numeric data into NaN
numeric_cols = ['val_a', 'val_b', 'val_c', 'target_id']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Handle merged cells (if any)
# df = df.ffill()
```

Step3 Run the multi-dimensional condition filtering logic to extract unique records matching specific numeric features.
```python
# Filtering logic: e.g. val_a, val_b, val_c must all meet a specific threshold (e.g. all zero)
mask = (df['val_a'] == 0) & (df['val_b'] == 0) & (df['val_c'] == 0)
filtered_df = df[mask][['target_id', 'val_a', 'val_b', 'val_c']]

# Extract unique IDs and drop nulls
result = filtered_df.drop_duplicates().dropna(subset=['target_id']).reset_index(drop=True)
```

Step4 Save the filtered result as a new Excel file and report its output path.
```python
output_path = "filtered_analysis_result.xlsx"

# Format the output column names
result.columns = ['Target_Index', 'Value_A', 'Value_B', 'Value_C']

# Export the file
result.to_excel(output_path, index=False)

# Print the result summary and the output path
print(f"Filtered records count: {len(result)}")
print(f"Result saved to: {output_path}")
```
