---
name: excel-basic-statistics-and-routing
description: "Basic statistics for multi-sheet Excel files: compute a conditional mean over filtered groups, extract data from a specified row range, deduplicate and sum it, and generate result files with their output paths."
---

## Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Filter a specified group, convert the target column to numeric type, and compute the mean.
```python
group_col = '班级'  # Placeholder example
target_group_value = '358'  # Placeholder example
target_cols = ['总分', '理数']  # Placeholder example

if group_col not in df_analysis.columns:
    raise ValueError(f"数据中缺少'{group_col}'列。")
df_analysis[group_col] = df_analysis[group_col].astype(str)
filtered_df = df_analysis[df_analysis[group_col] == target_group_value]

avg_scores = {}
for col in target_cols:
    if col not in filtered_df.columns:
        raise ValueError(f"数据中缺少'{col}'列。")
    try:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='raise')
        avg_scores[f'平均{col}'] = filtered_df[col].mean()
    except Exception as e:
        raise ValueError(f"列'{col}'无法转换为数值类型: {str(e)}")

output("筛选结果统计: " + str(avg_scores))
```

Step2 For small files, extract target fields from a specified row range of a specific sheet, deduplicate them, and compute the sum.
```python
unique_components = {}
total_power = 0

if total_rows < 10000:
    target_sheet = 'Sheet2'  # Placeholder example
    df_sheet2 = pd.read_excel(file_path, sheet_name=target_sheet)
    extracted_data = []
    
    # Extract range 1 (e.g. rows 21-28)
    for i in range(21, 29):
        if i < len(df_sheet2):
            row = df_sheet2.iloc[i]
            component = row.iloc[0]
            power = row.iloc[6]
            if pd.notna(component) and pd.notna(power):
                try:
                    extracted_data.append({'Component': component, 'Value': float(power)})
                except:
                    pass
    
    # Extract range 2 (e.g. rows 51-58)
    for i in range(51, 59):
        if i < len(df_sheet2):
            row = df_sheet2.iloc[i]
            component = row.iloc[0]
            power = row.iloc[1]
            if pd.notna(component) and pd.notna(power):
                try:
                    extracted_data.append({'Component': component, 'Value': float(power)})
                except:
                    pass
    
    # Merge and deduplicate (keep the first occurrence)
    for item in extracted_data:
        name = item['Component']
        val = item['Value']
        if name not in unique_components:
            unique_components[name] = val
    
    total_power = sum(unique_components.values())
```

Step3 Save the computed results, filtered data and statistics as Excel files and report their local output paths.
```python
import os

# Save the range extraction and summary results
if total_rows < 10000:
    result_df = pd.DataFrame([
        {'Component Name': name, 'Est. Power (kW)': power} 
        for name, power in unique_components.items()
    ])
    total_row = pd.DataFrame([{'Component Name': '合计', 'Est. Power (kW)': total_power}])
    result_df = pd.concat([result_df, total_row], ignore_index=True)
    
    output_path_power = "output_power_sum.xlsx"
    result_df.to_excel(output_path_power, index=False)
    output(f"功率计算结果已保存。下载链接: file://{os.path.abspath(output_path_power)}")

# Save the filtered and statistical results
output_path_analysis = "output_analysis_result.xlsx"
with pd.ExcelWriter(output_path_analysis, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, sheet_name="筛选数据", index=False)
    pd.DataFrame([avg_scores]).to_excel(writer, sheet_name="统计信息", index=False)

output(f"分析完成，结果已保存。下载链接: file://{os.path.abspath(output_path_analysis)}")
```
