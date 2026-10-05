---
name: dynamic-large-file-parquet-analysis
description: "Count the total Excel rows dynamically and convert to Parquet automatically when the data volume is large (>= 10,000 rows) to speed up reads, then run condition filtering, category summarization and result export on a target column, suited to rapid reading and statistical analysis of very large Excel files."
---

# Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Read the data dynamically (Parquet acceleration or a regular read).
```python
# If the excel-reading/large-excel-reading capability has been loaded, convert the Excel file to Parquet for faster reads
if 'da_large_file_analysis' in globals():
    # Assume the conversion produced a parquet file
    parquet_path = 'auto_converted_data.parquet'
    df = pd.read_parquet(parquet_path)
    print("已使用 Parquet 格式加速读取大文件。")
else:
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=0)
    print("文件较小，使用常规方式读取。")
```

Step2 Filter the target column by condition and summarize by the group column (including shares and a total).
```python
target_col = '目标列名'  # Example: '危险级别'
group_col = '分组列名'   # Example: '分项工程'
target_value = 'TARGET_VALUE'  # Example: '★★★★'

# Filter records containing the specific value
df_filtered = df[df[target_col].astype(str).str.contains(target_value, na=False)].copy()

# Category summary
result = df_filtered[group_col].value_counts()
result_df = pd.DataFrame({
    group_col: result.index,
    '数量': result.values
})

# Compute shares and add the total row
if not result_df.empty:
    result_df['占比'] = (result_df['数量'] / result_df['数量'].sum()).apply(lambda x: f"{x:.2%}")
    total_row = pd.DataFrame({
        group_col: ['总计'], 
        '数量': [result_df['数量'].sum()], 
        '占比': ['100.00%']
    })
    result_df = pd.concat([result_df, total_row], ignore_index=True)
```

Step3 Export the summary result and report the output path.
```python
output_path = 'filtered_summary_output.xlsx'

# Save the category summary as a spreadsheet file
result_df.to_excel(output_path, index=False)

# Report the plain output path for the user
print("数据处理与分类汇总完成。")
print(f"下载链接: {output_path}")
```
