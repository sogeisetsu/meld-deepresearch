---
name: outlier-detection-and-quality-assessment
description: "Run comprehensive outlier detection and data-quality assessment, identifying outliers with the IQR method and analyzing distribution shape via skewness and kurtosis, suited to preprocessing non-normal data."
---

### Step 1 Load the data and configure the environment
```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set Chinese/English fonts for visualization (SimHei or WenQuanYi)
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Load the data
file_path = 'data.xlsx'  # Replace with your actual file path
df = pd.read_excel(file_path)

# Basic information check
print(f"数据形状: {df.shape}")
print(f"数据类型:\n{df.dtypes}")
print(df.head())
```

### Step 2 Identify outliers with the IQR method
```python
# Automatically select numeric columns for analysis
target_cols = df.select_dtypes(include=[np.number]).columns.tolist()
outlier_summary = []

for col in target_cols:
    data = df[col].dropna()
    if data.empty:
        continue
        
    # Interquartile range computation (IQR)
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Identify outliers
    outliers = data[(data < lower_bound) | (data > upper_bound)]
    
    outlier_summary.append({
        'target_col': col,
        'outlier_count': len(outliers),
        'outlier_ratio': f"{(len(outliers)/len(data)*100):.2f}%",
        'lower_limit': lower_bound,
        'upper_limit': upper_bound,
        'sample_values': outliers.values.tolist()[:5]  # Keep the first 5 as examples
    })

outlier_df = pd.DataFrame(outlier_summary)
print("\n=== 异常值统计汇总 ===")
print(outlier_df.to_string(index=False))
```

### Step 3 Generate a multi-dimensional box plot
```python
# Configure the subplot layout
num_cols = len(target_cols)
cols_per_row = 3
rows = (num_cols + cols_per_row - 1) // cols_per_row

fig, axes = plt.subplots(rows, cols_per_row, figsize=(18, 5 * rows))
fig.suptitle('数据分布与异常值检测箱线图', fontsize=16, fontweight='bold')
axes_flat = axes.flatten()

# Walk each dimension and plot its distribution
for i, col in enumerate(target_cols):
    ax = axes_flat[i]
    # Draw and polish the box plot
    sns.boxplot(y=df[col].dropna(), ax=ax, color='skyblue', width=0.4,
                flierprops=dict(marker='o', markerfacecolor='red', markersize=5, alpha=0.5))
    
    ax.set_title(f'列: {col}', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Embed live statistics annotations
    stats = df[col].describe()
    stats_text = f'均值: {stats["mean"]:.2f}\n中位数: {stats["50%"]:.2f}\n标准差: {stats["std"]:.2f}'
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Hide the unused subplots
for j in range(i + 1, len(axes_flat)):
    axes_flat[j].axis('off')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
output_path = 'outlier_analysis_report.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
```

### Step 4 Skewness and kurtosis analysis with quality assessment
```python
# Analyze the distribution shape to inform cleaning decisions
print("=== 数据分布形态分析报告 ===")
quality_analysis = []

for col in target_cols:
    data = df[col].dropna()
    skewness = data.skew()
    kurtosis = data.kurtosis()
    
    # Classify the distribution shape
    skew_type = "右偏 (Positive)" if skewness > 0.5 else "左偏 (Negative)" if skewness < -0.5 else "对称"
    kurt_type = "尖峰 (Leptokurtic)" if kurtosis > 1 else "平峰 (Platykurtic)" if kurtosis < -1 else "正态趋向"
    
    quality_analysis.append({
        '字段': col,
        '偏度': round(skewness, 3),
        '峰度': round(kurtosis, 3),
        '分布形态': skew_type,
        '峰度特征': kurt_type
    })

analysis_df = pd.DataFrame(quality_analysis)
print(analysis_df.to_string(index=False))

# Export the analysis results
# analysis_df.to_csv('data_quality_report.csv', index=False)
```

### Step 5 Outlier handling suggestions (skeleton)
```python
def handle_outliers(df, col, method='cap'):
    """
    Skeleton function for outlier handling.
    method: 'cap' (winsorize), 'drop' (remove), 'none' (keep)
    """
    data = df[col].copy()
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    
    if method == 'cap':
        df[col] = df[col].clip(lower=lower, upper=upper)
    elif method == 'drop':
        df = df[(df[col] >= lower) & (df[col] <= upper)]
    
    return df

# Example: apply winsorization to a specific column
# df = handle_outliers(df, 'target_col', method='cap')
```
