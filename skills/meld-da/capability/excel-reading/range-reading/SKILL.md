---
name: range-reading-and-large-file-analysis
description: "Read a multi-sheet Excel file and choose the processing strategy dynamically by data volume, supporting specific-range extraction, large-file Parquet conversion, statistical analysis and visualization chart generation."
---

> **Note**: This sub-skill covers one step of the Excel analysis workflow. For the full pipeline (file reading, row counting, large-file optimization, export), see the parent workflow SKILL.md.

Step1 Clean data and count nulls for a specific sheet. Handles column names with spaces and computes the missing rate of key metrics.
```python
target_sheet = "Sheet2"
target_col = "是否通过"  # Example column name; replace it as needed

# Read the specified sheet
df_target = pd.read_excel(file_path, sheet_name=target_sheet)

# Clean the column names: trim surrounding spaces
df_target.columns = [str(col).strip() for col in df_target.columns]

if target_col in df_target.columns:
    null_count = df_target[target_col].isna().sum()
    print(f"'{target_col}' 列为空的数量: {null_count}")
    
    # Compute the shares
    stats = df_target[target_col].value_counts(dropna=False)
    print("分类统计结果：\n", stats)
else:
    print(f"未找到目标列: {target_col}")
```

Step2 Large-file optimization: convert the Excel file to Parquet to speed up later reads, and extract specific row/column ranges into a structured form.
```python
import numpy as np

output_dir = "output_results"
os.makedirs(output_dir, exist_ok=True)

if is_large_file:
    # Convert to Parquet
    parquet_path = os.path.join(output_dir, "temp_data.parquet")
    # Note: for large files, prefer chunked reads or selecting key columns
    df_full = pd.read_excel(file_path)
    df_full.to_parquet(parquet_path, engine='pyarrow', index=False)
    df = pd.read_parquet(parquet_path)
else:
    df = pd.read_excel(file_path)

# Extract a specific data range (e.g. rows 40-50, two specific columns)
# Simulate extracting value pairs from a non-standard table
data_rows = []
x_col_idx, y_col_idx = 0, 1 # Assume the target data is in columns 0 and 1

for i in range(40, min(50, len(df))):
    row = df.iloc[i]
    try:
        # Clean the strings and convert to floats
        val_x = float(str(row.iloc[x_col_idx]).replace(' ', ''))
        val_y = float(str(row.iloc[y_col_idx]).replace(' ', ''))
        if pd.notna(val_x) and pd.notna(val_y):
            data_rows.append((val_x, val_y))
    except (ValueError, TypeError):
        continue

analysis_df = pd.DataFrame(data_rows, columns=['target_x', 'target_y'])
```

Step3 Run advanced statistical analysis and visualization: linear regression fitting, Chinese/English font configuration, high-resolution chart saving and output path reporting.
```python
import matplotlib.pyplot as plt

# Configure a Chinese font (works across environments)
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

if not analysis_df.empty:
    x = analysis_df['target_x'].values
    y = analysis_df['target_y'].values
    
    # 1. Linear fit
    coeffs = np.polyfit(x, y, 1)
    poly_func = np.poly1d(coeffs)
    trend_line = poly_func(x)
    
    # 2. Chart polish
    plt.figure(figsize=(10, 6), dpi=300)
    plt.scatter(x, y, color='#1f77b4', s=60, label='原始数据点', alpha=0.7)
    plt.plot(x, trend_line, color='#d62728', lw=2, label=f'趋势线: y={coeffs[0]:.4f}x+{coeffs[1]:.4f}')
    
    plt.title("数据分布与线性回归分析", fontsize=14, pad=20)
    plt.xlabel("维度 X", fontsize=12)
    plt.ylabel("维度 Y", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    
    chart_path = os.path.join(output_dir, "analysis_chart.png")
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    
    # 3. Export the results
    result_path = os.path.join(output_dir, "analysis_results.csv")
    analysis_df['trend_prediction'] = trend_line
    analysis_df.to_csv(result_path, index=False, encoding='utf-8-sig')
    
    # 4. Report the plain output paths
    print(f"分析图表已保存: {chart_path}")
    print(f"结构化数据已保存: {result_path}")
    print(f"拟合方程: y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}")
else:
    print("未提取到有效数值数据，跳过可视化步骤")
```
