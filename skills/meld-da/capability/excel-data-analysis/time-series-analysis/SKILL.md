---
name: time-series-and-categorical-analysis
description: "Run multi-dimensional trend analysis, percentage cleaning, performance grading and forecasting on time-series or categorical data, and produce a high-resolution combined visualization report, suited to business metric monitoring and forecasting."
---

## Skill Steps

Step1 Load and inspect the raw data, and configure a Chinese font so charts render correctly.
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set a Chinese font that works across operating systems
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Load the Excel file
file_path = 'data.xlsx'
df = pd.read_excel(file_path)

print(f"数据形状: {df.shape}")
print(f"列名: {list(df.columns)}")
```

Step2 Extract time-series or categorical dimension data, handle percentage formats, and compute the trend.
```python
def convert_percentage(pct_str):
    """Convert a percentage string to a number, handling nulls and non-string types"""
    if pd.isna(pct_str):
        return None
    if isinstance(pct_str, str) and '%' in pct_str:
        try:
            return float(pct_str.replace('%', ''))
        except ValueError:
            return None
    return pct_str

time_col = '时间列'  # Placeholder example
target_cols = ['指标1占比', '指标2占比', '指标3占比']  # Placeholder example

# Convert percentage strings to numbers and extract the data
ts_df = df[[time_col] + target_cols].copy() if time_col in df.columns else df.copy()
for col in target_cols:
    if col in ts_df.columns:
        ts_df[col] = ts_df[col].apply(convert_percentage)
        
        # Compute the change and label the state
        diff_col = f'{col}_变化'
        trend_col = f'{col}_趋势'
        ts_df[diff_col] = ts_df[col].diff()
        ts_df[trend_col] = ['上升' if x > 0 else '下降' if x < 0 else '稳定' for x in ts_df[diff_col]]
```

Step3 Model multi-dimensional grading on the numeric values, map differentiated growth rates, and compute forecasts.
```python
group_col = '分组列'  # Placeholder example, e.g. '部门'
value_col = '数值列'  # Placeholder example, e.g. '销售额'

# Aggregate the sums and sort
grouped_df = df.groupby(group_col, as_index=False)[value_col].sum()
grouped_df = grouped_df.sort_values(by=value_col, ascending=False).reset_index(drop=True)

# Multi-dimensional grading structure: top 30% high, middle 40% medium, bottom 30% low
total_rows = len(grouped_df)
high_threshold = int(total_rows * 0.3)
mid_threshold = int(total_rows * 0.7)

grouped_df['等级'] = np.where(
    grouped_df.index < high_threshold, '高',
    np.where(grouped_df.index < mid_threshold, '中', '低')
)

# Category mapping function skeleton: differentiated growth rates per grade
growth_rates = {'高': 0.15, '中': 0.08, '低': 0.03}
grouped_df['增长率'] = grouped_df['等级'].map(growth_rates)

# Compute the forecast and the growth amount
grouped_df['预测值'] = grouped_df[value_col] * (1 + grouped_df['增长率'])
grouped_df['增长量'] = grouped_df['预测值'] - grouped_df[value_col]
```

Step4 Generate multi-dimensional charts (stacked area, bar, horizontal bar) and save them as high-resolution images.
```python
output_path = 'trend_analysis_report.png'
plt.figure(figsize=(14, 10))

# Subplot 1: stacked area chart (share change over time)
plt.subplot(2, 2, 1)
sns.set_style('whitegrid')
if time_col in ts_df.columns and all(c in ts_df.columns for c in target_cols):
    plt.stackplot(ts_df[time_col], 
                  *[ts_df[c] for c in target_cols], 
                  labels=target_cols, alpha=0.8)
    plt.title('各指标占比变化趋势', fontsize=14, fontweight='bold')
    plt.xlabel(time_col)
    plt.ylabel('占比 (%)')
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)

# Subplot 2: current vs forecast comparison (bar chart)
plt.subplot(2, 2, 2)
x = np.arange(len(grouped_df))
width = 0.35
plt.bar(x - width/2, grouped_df[value_col], width, label='当前值', alpha=0.8)
plt.bar(x + width/2, grouped_df['预测值'], width, label='预测值', alpha=0.8)
plt.xlabel(group_col)
plt.ylabel('数值')
plt.title('当前与预测值对比')
plt.xticks(x, grouped_df[group_col], rotation=45)
plt.legend()

# Subplot 3: growth-rate distribution (horizontal bar)
plt.subplot(2, 2, 3)
plt.barh(grouped_df[group_col], grouped_df['增长率'], color='skyblue')
plt.xlabel('增长率')
plt.title('各组增长率分布')
plt.gca().invert_yaxis()

# Subplot 4: growth-amount distribution (bar)
plt.subplot(2, 2, 4)
plt.bar(grouped_df[group_col], grouped_df['增长量'], color='lightcoral')
plt.xlabel(group_col)
plt.ylabel('增长量')
plt.title('各组增长量分析')
plt.xticks(rotation=45)

plt.tight_layout()
# Polish the chart and save at high resolution
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()
```

Step5 Generate a combined analysis report summarizing the key metrics and the trend conclusion.
```python
# Overall forecast summary
total_current = grouped_df[value_col].sum()
total_forecast = grouped_df['预测值'].sum()
total_growth = grouped_df['增长量'].sum()
overall_growth_rate = (total_forecast - total_current) / total_current if total_current else 0

print("=" * 60)
print("📊 综合趋势分析报告")
print("=" * 60)
print(f"当前总值: {total_current:,.2f}")
print(f"预测总值: {total_forecast:,.2f}")
print(f"总增长量: {total_growth:,.2f}")
print(f"整体增长率: {overall_growth_rate:.2%}")
print("\n📈 分析结论：")
if overall_growth_rate > 0.1:
    print("  - 整体趋势向好，预计实现显著增长。")
elif overall_growth_rate > 0:
    print("  - 呈温和增长态势，建议加强低等级组支持。")
else:
    print("  - 预测下滑，需深入分析原因并制定应对策略。")
print("=" * 60)
```
