---
name: excel-sheet-filter-export
description: "Count rows of a multi-sheet Excel file dynamically to decide the large-file handling logic, filter records by specific conditions, rename fields and export a new Excel file with its output path, suited to multi-sheet data exploration and condition-filtered export."
---

## Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Read the target sheet, clean field formats, filter records by specific conditions, and compute key metrics.
```python
target_sheet = 'Sheet1' # Replace with your actual sheet name
df_target = pd.read_excel(file_path, sheet_name=target_sheet)

# Clean the string format of the target column (trim surrounding spaces)
filter_col = 'group_col'
if filter_col in df_target.columns:
    df_target[filter_col] = df_target[filter_col].astype(str).str.strip()

# Filter records matching the condition
target_value = 'target_value_example'
mask = df_target[filter_col] == target_value
df_filtered = df_target[mask]

# Count distinct values in the specific range
target_col = 'target_col'
if target_col in df_filtered.columns:
    specific_ranges = df_filtered[target_col].dropna().unique()
    print(f"{target_col} 种类数量:", len(specific_ranges))
    
    # Count each category and compute its share
    value_counts_df = df_filtered[target_col].value_counts().reset_index()
    value_counts_df.columns = [target_col, '数量']
    value_counts_df['占比'] = (value_counts_df['数量'] / value_counts_df['数量'].sum()).map('{:.2%}'.format)
    
    # Add the total row
    total_row = pd.DataFrame({
        target_col: ['总计'], 
        '数量': [value_counts_df['数量'].sum()], 
        '占比': ['100.00%']
    })
    value_counts_df = pd.concat([value_counts_df, total_row], ignore_index=True)
    print(f"\n{target_col} 分布情况:\n", value_counts_df.head())
```

Step2 Extract the needed fields, rename and format the result, save it as a new Excel file, and report the output path.
```python
# Extract the needed columns and rename them
selected_cols = ['col1', 'col2', filter_col, target_col]
# Ensure the columns exist
existing_cols = [col for col in selected_cols if col in df_filtered.columns]
result_df = df_filtered[existing_cols].copy()

# Field renaming mapping dictionary
rename_mapping = {
    'col1': '重命名列1',
    'col2': '重命名列2',
    filter_col: '筛选维度',
    target_col: '分析维度'
}
result_df = result_df.rename(columns=rename_mapping)

# Save the result and report its path
output_path = "filtered_result_output.xlsx"
result_df.to_excel(output_path, index=False)
print("结果已保存至:", output_path)
print(f"Result file: {output_path}")
```
