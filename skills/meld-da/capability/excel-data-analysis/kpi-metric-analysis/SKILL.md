---
name: large-file-kpi-analysis
description: "Choose the reading strategy automatically by data volume (large files go through Parquet), extract key metrics for unit-consistency validation and ranking analysis, and output a result table with its output path."
---

## Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Extract key metrics, validate the unit consistency of physical quantities/metrics, and sort core business metrics in descending order.
```python
# 1. Unit consistency validation and computation for quantities/metrics (formula structure kept as an example)
col_numerator = 'numerator_col'  # Example: Mx (kN·m)
col_denominator = 'denominator_col' # Example: Wx (cm³)
col_target = 'target_col' # Example: sigma (MPa)

if col_numerator in data.columns and col_denominator in data.columns and col_target in data.columns:
    # Unit conversion example: convert to standard units before computing
    data['den_converted'] = data[col_denominator] * 1e-6
    data['num_converted'] = data[col_numerator] * 1e3
    data['calc_result_pa'] = data['num_converted'] / data['den_converted']
    data['calc_result_mpa'] = data['calc_result_pa'] / 1e6
    
    # Tolerance validation
    tolerance = 1e-6
    data['is_valid'] = abs(data['calc_result_mpa'] - data[col_target]) < tolerance
    print("单位一致性验证通过率:", data['is_valid'].mean() * 100, "%")

# 2. Extract the key metrics and sort descending
group_col = 'group_col' # Example: development zone name
metric_col = 'metric_col' # Example: actual foreign capital received

result_df = pd.DataFrame()
if group_col in data.columns and metric_col in data.columns:
    result_df = data[[group_col, metric_col]].copy()
    result_df = result_df.sort_values(metric_col, ascending=False).reset_index(drop=True)
```

Step2 Assemble the analysis and validation results into a final DataFrame, save it as an Excel file, and report its output path.
```python
output_path = 'analysis_result.xlsx'

# Decide which DataFrame to output
if not result_df.empty:
    result_df_final = result_df
elif 'calc_result_mpa' in data.columns:
    result_df_final = data[[col_numerator, col_denominator, col_target, 'calc_result_mpa', 'is_valid']].copy()
    result_df_final.columns = ['分子指标', '分母指标', '目标比对值', '计算结果', '是否一致']
else:
    result_df_final = data.head(100) # Default: output the first 100 rows as an example

# Save as an Excel file
result_df_final.to_excel(output_path, index=False, engine='openpyxl')
print(f"分析结果已保存至: {output_path}")

# Report the plain output path
print(f"下载链接: [点击下载分析结果](./{output_path})")
```
