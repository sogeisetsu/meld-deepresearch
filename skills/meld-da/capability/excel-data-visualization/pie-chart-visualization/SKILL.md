---
name: pie-chart-data-analysis
description: "Run category summary statistics on multi-sheet Excel or CSV data, automatically detect key fields, and generate an analysis report with shares, values and a polished pie chart plus its output path."
---

Step1 Read the file and count the rows of all sheets to confirm the data scale and decide the processing strategy.
```python
import pandas as pd

file_path = input_file
total_rows = 0
sheet_names = []

try:
    if file_path.endswith('.xlsx'):
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        # Count total rows across all worksheets
        for sheet in sheet_names:
            df_tmp = pd.read_excel(file_path, sheet_name=sheet)
            total_rows += len(df_tmp)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        total_rows = len(df)
    else:
        raise ValueError("不支持的文件格式，仅支持 .xlsx 或 .csv")
except Exception as e:
    raise RuntimeError(f"文件读取失败: {e}")

is_large_file = total_rows >= 10000
```

Step2 Automatically detect the category and value columns, and clean and convert the data.
```python
import re

# Load the first valid dataset
if file_path.endswith('.xlsx'):
    df = pd.read_excel(file_path, sheet_name=sheet_names[0])
else:
    df = pd.read_csv(file_path)

# 1. Detect the numeric target column (e.g. amount, expense, score, quantity)
target_keywords = ['金额', '支出', '造价', '经费', '数量', '得分']
target_cols = [col for col in df.columns if any(k in col for k in target_keywords)]
target_col = target_cols[0] if target_cols else df.select_dtypes(include=['number']).columns[0]

# 2. Detect the category column (regex supports Chinese ordinals or specific category markers)
category_pattern = re.compile(r'[一二三四五六七八九十百]+|地区|类别|类型|状态')
category_cols = [col for col in df.columns if category_pattern.search(col)]
category_col = category_cols[0] if category_cols else df.select_dtypes(include=['object']).columns[0]

# 3. Data cleaning: handle merged-cell fills, missing values and type conversion
df[category_col] = df[category_col].ffill() # Handle Excel merged cells
df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
clean_df = df[[category_col, target_col]].dropna()
clean_df.columns = ['category', 'value']
```

Step3 Run multi-dimensional aggregation, computing shares and summary statistics.
```python
# Category summary
summary_df = clean_df.groupby('category', as_index=False)['value'].sum()
total_val = summary_df['value'].sum()

# Compute and format the shares
summary_df['percentage'] = (summary_df['value'] / total_val * 100).round(2)
summary_df = summary_df.sort_values(by='value', ascending=False)

# Build the total row (optional)
total_row = pd.DataFrame([['总计', total_val, 100.0]], columns=summary_df.columns)
display_df = pd.concat([summary_df, total_row], ignore_index=True)
```

Step4 Generate a polished pie chart and export an Excel report with the chart embedded.
```python
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from openpyxl.drawing.image import Image

# Configure Chinese/English fonts
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(10, 7), dpi=120)
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']

# Highlight the largest share
explode = [0.05 if i == 0 else 0 for i in range(len(summary_df))]

wedges, texts, autotexts = ax.pie(
    summary_df['value'],
    labels=summary_df['category'],
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    explode=explode,
    shadow=True,
    pctdistance=0.85
)

# Add a white center circle (donut effect)
centre_circle = plt.Circle((0,0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)

plt.title(f'{target_col} 分布分析', fontsize=15, pad=20)
ax.legend(wedges, summary_df['category'], title="分类明细", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

# Save the chart into memory
img_buffer = BytesIO()
plt.savefig(img_buffer, format='png', bbox_inches='tight')
plt.close()

# Write to Excel and embed the chart
output_path = 'analysis_report.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    display_df.to_excel(writer, sheet_name='统计汇总', index=False)
    ws = writer.book['统计汇总']
    img_buffer.seek(0)
    img = Image(img_buffer)
    ws.add_image(img, 'E2')

# Build a Base64 link for the file
with open(output_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
download_url = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"

print(f"分析完成。总行数: {total_rows}，下载链接已生成。")
```
