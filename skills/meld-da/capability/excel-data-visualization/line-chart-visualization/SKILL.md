---
name: line-chart-visualization
description: "Extract structured data and run feature cleaning and clustering analysis, generating multi-dimensional combined visualizations covering trend comparison, distribution shape and parameter sensitivity, suited to forecasting and multi-dimensional comparison scenarios."
---

Step1 Data loading and preprocessing (with large-file Parquet conversion and dynamic header detection).
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import re

# Configure Chinese/English fonts and polish the charts
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

file_path = 'input_data.xlsx'

# Handle large Excel files: count total rows and convert to Parquet when >= 10,000 for efficiency
xls = pd.ExcelFile(file_path)
total_rows = sum(pd.read_excel(xls, sheet_name=s, header=None).shape[0] for s in xls.sheet_names)

if total_rows >= 10000:
    parquet_path = "temp_converted_file.parquet"
    with pd.ExcelWriter(parquet_path, engine='pyarrow') as writer:
        for sheet in xls.sheet_names:
            df_sheet = pd.read_excel(xls, sheet_name=sheet, header=None)
            df_sheet.to_excel(writer, sheet_name=sheet, index=False, header=False)
    df = pd.read_excel(parquet_path, sheet_name='Sheet1', header=None)
else:
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

# Dynamically detect the header and extract the data
header_row_idx = None
target_cols = ['group_col', 'value_col1', 'value_col2'] # Placeholder example column names
for idx, row in df.iterrows():
    row_vals = row.astype(str).tolist()
    if all(col in row_vals for col in target_cols):
        header_row_idx = idx
        break

if header_row_idx is not None:
    df.columns = df.iloc[header_row_idx].tolist()
    df_clean = df.iloc[header_row_idx + 1:].reset_index(drop=True)
else:
    df_clean = df.copy()
```

Step2 Data cleaning and feature engineering (regex extraction, missing-value handling and merged-cell restoration).
```python
# Merged-cell handling (ffill + walk to restore)
if 'group_col' in df_clean.columns:
    df_clean['group_col'] = df_clean['group_col'].ffill()

# Data cleaning regex: extract numbers
if 'value_col1' in df_clean.columns:
    df_clean['value_col1'] = df_clean['value_col1'].astype(str).str.replace(r'[^\d.]', '', regex=True)
    df_clean['value_col1'] = pd.to_numeric(df_clean['value_col1'], errors='coerce')

df_clean = df_clean.dropna(subset=['value_col1']).reset_index(drop=True)

# Category mapping function skeleton
def map_category(val):
    if pd.isna(val): return 'Unknown'
    if val > 100: return 'High' # Placeholder example
    elif val > 50: return 'Medium'
    return 'Low'

if 'value_col1' in df_clean.columns:
    df_clean['level'] = df_clean['value_col1'].apply(map_category)

# Multi-dimensional scoring/grading algorithm structure
def calculate_score(row):
    score = 0
    if pd.notna(row.get('value_col1')) and float(row['value_col1']) > 50: # Placeholder example
        score += 50
    if pd.notna(row.get('value_col2')) and float(row['value_col2']) < 10: # Placeholder example
        score += 50
    return score

df_clean['comprehensive_score'] = df_clean.apply(calculate_score, axis=1)
```

Step3 Clustering and cross statistics (standardization, KMeans and multi-dimensional cross analysis).
```python
numeric_cols = ['value_col1', 'comprehensive_score']
existing_num_cols = [c for c in numeric_cols if c in df_clean.columns]

if existing_num_cols:
    # Standardize the numeric features
    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(df_clean[existing_num_cols].fillna(0))
    
    # Clustering to reveal latent group structures
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_clean['cluster_label'] = kmeans.fit_predict(numeric_scaled)

# value_counts + share computation
if 'level' in df_clean.columns:
    level_counts = df_clean['level'].value_counts()
    level_ratio = df_clean['level'].value_counts(normalize=True) * 100
    summary_df = pd.DataFrame({'频次': level_counts, '占比(%)': level_ratio.round(2)})
    summary_df.loc['总计'] = summary_df.sum()
    print("分类统计汇总:\n", summary_df)

# Cross analysis crosstab/pivot
if 'cluster_label' in df_clean.columns and 'level' in df_clean.columns:
    cross_tb = pd.crosstab(df_clean['cluster_label'], df_clean['level'], margins=True, margins_name='总计')
    print("\n聚类与等级交叉分析:\n", cross_tb)
```

Step4 Multi-dimensional visualization and result output (trend, distribution, share and sensitivity charts).
```python
# Create the multi-dimensional combined visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=150)
fig.suptitle('综合数据分析图表', fontsize=16)

group_col = 'group_col' if 'group_col' in df_clean.columns else df_clean.columns[0]

# 1. Trend comparison line chart
if 'value_col1' in df_clean.columns:
    axes[0, 0].plot(df_clean[group_col].astype(str).str[:10], df_clean['value_col1'], marker='o', label='指标1', color='#1f77b4')
    if 'comprehensive_score' in df_clean.columns:
        axes[0, 0].plot(df_clean[group_col].astype(str).str[:10], df_clean['comprehensive_score'], marker='s', label='综合评分', color='#ff7f0e')
    axes[0, 0].set_title('多指标趋势对比')
    axes[0, 0].set_xlabel('分组维度')
    axes[0, 0].set_ylabel('数值')
    axes[0, 0].legend(loc='upper right')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].tick_params(axis='x', rotation=45)

# 2. Distribution histogram
if 'value_col1' in df_clean.columns:
    axes[0, 1].hist(df_clean['value_col1'].dropna(), bins=15, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 1].set_title('数值分布特征')
    axes[0, 1].set_xlabel('数值区间')
    axes[0, 1].set_ylabel('频次')
    axes[0, 1].grid(True, alpha=0.3)

# 3. Market share / composition pie chart
if 'level' in df_clean.columns:
    level_counts = df_clean['level'].value_counts()
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(level_counts)))
    axes[1, 0].pie(level_counts, labels=level_counts.index, autopct='%1.1f%%', colors=colors_pie, startangle=90)
    axes[1, 0].set_title('分类占比分布')

# 4. Parameter sensitivity / clustering scatter plot
if 'cluster_label' in df_clean.columns and 'value_col1' in df_clean.columns:
    sns.scatterplot(data=df_clean, x=group_col, y='value_col1', hue='cluster_label', ax=axes[1, 1], palette='Set1', s=80)
    axes[1, 1].set_title('聚类分组散点图')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save the chart and the cleaned data
chart_path = "output_chart.png"
output_path = "output_table.xlsx"

plt.savefig(chart_path, dpi=300, bbox_inches='tight')
plt.close()

df_clean.to_excel(output_path, index=False)

# Report the plain output paths
print(f"分析完成。")
print(f"图表下载链接: file:///{os.path.abspath(chart_path)}")
print(f"数据下载链接: file:///{os.path.abspath(output_path)}")
```
