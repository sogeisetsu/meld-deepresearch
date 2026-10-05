---
name: multi-file-excel-parquet-analysis
description: "Read a multi-sheet Excel file and measure its scale, supporting large-file conversion to Parquet, categorical statistics and visualization report generation."
---


> **Note**: This sub-skill covers one step of the Excel analysis workflow. For the full pipeline (file reading, row counting, large-file optimization, export), see the parent workflow SKILL.md.


Step1 Read the Excel file, walk all sheets to count rows, and assess the data scale.
```python
import pandas as pd
import os

file_path = "input_data.xlsx"  # Replace with your actual file path

if not os.path.exists(file_path):
    print(f"Error: 文件 {file_path} 不存在")
else:
    # Get all sheet names
    xl = pd.ExcelFile(file_path)
    sheet_names = xl.sheet_names
    print("Sheet 列表:", sheet_names)
    
    total_rows = 0
    for sheet in sheet_names:
        # Read only the first column for a fast row count, avoiding OOM on large files
        df_tmp = pd.read_excel(file_path, sheet_name=sheet, usecols=[0])
        row_count = len(df_tmp)
        total_rows += row_count
        print(f"Sheet: {sheet}, 行数: {row_count}")
    
    print(f"总行数汇总: {total_rows}")
```

Step2 Read the converted data, run categorical statistics, and compute frequencies and shares.
```python
import pandas as pd

# Read the Parquet file
df_analyzed = pd.read_parquet(output_parquet)

# Define the target statistics column (e.g. '剪裁结果', '状态')
target_col = '剪裁结果' 

if target_col in df_analyzed.columns:
    # Count each category and compute its share
    counts = df_analyzed[target_col].value_counts()
    percent = df_analyzed[target_col].value_counts(normalize=True) * 100
    
    # Build the statistics table and add a total row
    summary_df = pd.DataFrame({
        '分类': counts.index,
        '数量': counts.values,
        '占比(%)': percent.values.round(2)
    })
    
    # Add the total row
    total_row = pd.DataFrame([['总计', summary_df['数量'].sum(), 100.0]], columns=summary_df.columns)
    summary_df = pd.concat([summary_df, total_row], ignore_index=True)
    
    print("统计摘要:\n", summary_df)
else:
    print(f"未找到目标列: {target_col}")
```

Step3 Generate a pie chart, save the analysis report, and report the result paths.
```python
import matplotlib.pyplot as plt

# Configure a Chinese font (practical tip: prevents garbled chart text)
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

if target_col in df_analyzed.columns:
    # Draw the pie chart
    plt.figure(figsize=(10, 7), dpi=100)
    plot_data = df_analyzed[target_col].value_counts()
    plt.pie(plot_data, labels=plot_data.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title(f'{target_col} 分布占比')
    
    # Save the chart
    chart_output = "analysis_pie_chart.png"
    plt.savefig(chart_output, bbox_inches='tight')
    
    # Save the statistics as Excel
    report_output = "analysis_report.xlsx"
    summary_df.to_excel(report_output, index=False)
    
    print(f"分析图表已保存: {chart_output}")
    print(f"统计表格已保存: {report_output}")
    
    # Report the plain output path (for report display)
    print(f"下载链接: {os.path.abspath(report_output)}")
```
