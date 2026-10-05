---
name: numeric-format-normalization
description: "Normalize and clean numeric formats in Excel data, support the Parquet conversion flow for large data, and complete key-metric total reconciliation with result file export."
---

## Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Clean the target column (drop nulls, normalize numeric formats), compute the total, and reconcile it precisely against the total row in the designated summary sheet.
```python
target_col = '目标数值列'  # Example: '建筑面积'
summary_sheet_name = 'Summary' # Example summary sheet name
summary_item_col = '项目'
summary_value_col = '数值'

# Data cleaning: drop nulls and force numeric conversion
df_cleaned = df_processed.dropna(subset=[target_col]).copy()
df_cleaned[target_col] = pd.to_numeric(df_cleaned[target_col], errors='coerce')

# Compute the total
total_calculated = df_cleaned[target_col].sum()

# Read the "合 计" row from the designated sheet and reconcile
try:
    summary_sheet = pd.read_excel(file_path, sheet_name=summary_sheet_name)
    expected_total = summary_sheet.loc[summary_sheet[summary_item_col] == '合 计', summary_value_col].values[0]
    
    # Check consistency (handles floating-point precision)
    if abs(total_calculated - expected_total) < 1e-6:
        consistency = "一致"
        difference = 0
    else:
        consistency = "不一致"
        difference = abs(total_calculated - expected_total)
    
    print(f"计算合计: {total_calculated}, 指定合计: {expected_total}, 一致性: {consistency}")
except Exception as e:
    print(f"核对失败: {e}")
    expected_total = None
    consistency = "未知"
    difference = None
```

Step2 Save the analysis and reconciliation results as spreadsheet files and report their plain output paths.
```python
output_path_xlsx = 'analysis_result.xlsx'
output_path_csv = 'analysis_result.csv'

# Build the result table
result_data = {
    '统计项': ['总行数', f'{target_col}合计（计算值）', f'{target_col}合计（指定值）', '一致性', '差异值'],
    '数值': [total_rows, total_calculated, expected_total, consistency, difference]
}
result_df = pd.DataFrame(result_data)

# Save in multiple formats
result_df.to_excel(output_path_xlsx, index=False)
result_df.to_csv(output_path_csv, index=False, encoding='utf-8-sig')

# Report the plain output paths (shown in the report)
print("分析结果已保存，可下载：")
print(f"- {output_path_xlsx}")
print(f"- {output_path_csv}")
```
