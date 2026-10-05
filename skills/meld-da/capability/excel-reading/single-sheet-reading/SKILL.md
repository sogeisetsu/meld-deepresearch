---
name: single-sheet-reading-and-analysis
description: "Read and parse a single Excel worksheet with merged-cell handling, data cleaning, cross analysis and multi-dimensional visualization, suited to extracting key metrics from one sheet for trend simulation and chart generation."
---

## Skill Steps

Step1 Import dependencies and configure Chinese/English fonts to prevent garbled chart text
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import base64
from IPython.display import HTML

# Set Chinese/English fonts
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
```

Step2 Load the data and clean it, including merged-cell handling and regex extraction
```python
def load_and_clean_data(file_path, sheet_name=0):
    # Read the data
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Handle merged cells: forward fill and restore
    # df['group_col'] = df['group_col'].ffill()
    
    # Standardize column names: strip spaces and newlines
    df.columns = [str(col).strip().replace('\n', '') for col in df.columns]
    
    # Data cleaning regex example: extract numbers
    if 'target_col' in df.columns:
        df['target_col'] = df['target_col'].astype(str).apply(lambda x: re.sub(r'[^\d.]', '', x))
        df['target_col'] = pd.to_numeric(df['target_col'], errors='coerce')
    
    # Drop fully empty rows
    df = df.dropna(how='all')
    return df
```

Step3 Category mapping and multi-dimensional scoring/grading algorithm
```python
def categorize_and_score(df, target_col):
    # Category mapping function skeleton
    def map_category(val):
        if pd.isna(val):
            return '未知'
        elif val > 100:  # Placeholder example: high threshold
            return 'A类'
        elif val > 50:   # Placeholder example: medium threshold
            return 'B类'
        else:
            return 'C类'
    
    if target_col in df.columns:
        df['category'] = df[target_col].apply(map_category)
    
    # Multi-dimensional scoring/grading algorithm structure
    # df['score'] = df['metric1'] * 0.4 + df['metric2'] * 0.6
    return df
```

Step4 Cross analysis and statistics summary (frequency, share, total row)
```python
def analyze_data(df, group_col):
    # value_counts + share + total row
    counts = df[group_col].value_counts().reset_index()
    counts.columns = [group_col, '数量']
    counts['占比'] = (counts['数量'] / counts['数量'].sum()).map('{:.2%}'.format)
    
    # Add the total row
    total_row = pd.DataFrame({
        group_col: ['总计'], 
        '数量': [counts['数量'].sum()], 
        '占比': ['100.00%']
    })
    counts = pd.concat([counts, total_row], ignore_index=True)
    
    # Cross analysis crosstab/pivot
    if 'category' in df.columns:
        cross_tb = pd.crosstab(df[group_col], df['category'], margins=True, margins_name='总计')
    else:
        cross_tb = None
        
    return counts, cross_tb
```

Step5 Chart polish and high-resolution output
```python
def visualize_results(df, group_col, target_col, output_path):
    # High resolution: dpi=300
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Color scheme and chart drawing
    valid_data = df.dropna(subset=[group_col, target_col])
    colors = sns.color_palette("husl", len(valid_data[group_col].unique()))
    sns.barplot(data=valid_data, x=group_col, y=target_col, palette=colors, ax=ax)
    
    # Label positions and polish
    ax.set_title('多维度数据分析', fontsize=16, pad=15)
    ax.set_xlabel('分组维度', fontsize=12)
    ax.set_ylabel('目标指标', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add data labels
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

Step6 Large-file Parquet conversion and output link generation
```python
def export_and_generate_link(df, output_path):
    # Large-file Parquet conversion
    parquet_path = output_path.replace('.png', '.parquet').replace('.csv', '.parquet')
    df.to_parquet(parquet_path, index=False)
    
    # Generate an inline download link
    csv_data = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv_data).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="analysis_result.csv">点击下载分析结果 (CSV)</a>'
    display(HTML(href))
```
