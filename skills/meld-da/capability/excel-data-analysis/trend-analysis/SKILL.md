---
name: trend-analysis
description: "Run graded evaluation and trend forecasting on multi-dimensional data, compute forecasts with differentiated growth rates, and generate comparison visualizations, suited to performance evaluation and goal setting."
---

Step1 Load the data and configure the environment, setting a Chinese font so visualizations render correctly.
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Set a Chinese font: prefer WenQuanYi Zen Hei, fall back to SimHei and DejaVu Sans
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Load the data file
file_path = 'your_data.xlsx'
df = pd.read_excel(file_path)

print(f"数据形状: {df.shape}")
df.head()
```

Step2 Grade the data by performance, assign differentiated growth rates, and compute the forecast.
```python
# Define generic column names
group_col = '分组列名'  # Example: '部门', '产品线'
target_col = '目标数值列名'  # Example: '销售额', '产量'

# Compute the total per dimension and sort
performance_data = df.groupby(group_col, as_index=False)[target_col].sum().sort_values(by=target_col, ascending=False)

# Assign grades (top 30% high, bottom 30% low, the rest medium)
n = len(performance_data)
high_perf_threshold = int(0.3 * n)
low_perf_threshold = int(0.7 * n)

performance_data['等级'] = '中等'
performance_data.loc[:high_perf_threshold-1, '等级'] = '高'
performance_data.loc[low_perf_threshold:, '等级'] = '低'

# Growth-rate mapping dictionary for the forecast
growth_rate_map = {
    '高': 0.10,   # 10% growth rate
    '中等': 0.08, # 8% growth rate
    '低': 0.15    # 15% growth rate
}
performance_data['预测增长率'] = performance_data['等级'].map(growth_rate_map)

# Forecast = current * (1 + growth rate), rounded to two decimals
performance_data['预测值'] = (performance_data[target_col] * (1 + performance_data['预测增长率'])).round(2)
performance_data[[group_col, target_col, '预测增长率', '预测值']].head()
```

Step3 Analyze the forecast results, compute the overall trend metrics, and derive a conclusion.
```python
# Compute the overall metrics
current_total = performance_data[target_col].sum()
forecast_total = performance_data['预测值'].sum()
growth_rate_total = (forecast_total - current_total) / current_total if current_total != 0 else 0

print(f"当前总计: {current_total:,.2f}")
print(f"预测总计: {forecast_total:,.2f}")
print(f"整体增长率: {growth_rate_total:.2%}")

# Derive the trend conclusion
if growth_rate_total > 0.1:
    conclusion = "整体趋势向好，预计实现显著增长。"
elif growth_rate_total > 0:
    conclusion = "整体呈温和增长态势。"
else:
    conclusion = "整体面临压力，需重点关注低绩效部分。"

print(f"趋势结论：{conclusion}")
```

Step4 Visualize the forecast with a horizontal bar chart comparing current and predicted values, annotated with grades and numbers.
```python
# Set figure size and high resolution
plt.figure(figsize=(12, 8), dpi=100)

# Horizontal bar chart: current vs forecast
x_pos = np.arange(len(performance_data))
width = 0.35

plt.barh(x_pos - width/2, performance_data[target_col], width, label='当前值', color='skyblue', edgecolor='black', alpha=0.8)
plt.barh(x_pos + width/2, performance_data['预测值'], width, label='预测值', color='lightcoral', edgecolor='black', alpha=0.8)

# Add value labels
for i, (current, forecast) in enumerate(zip(performance_data[target_col], performance_data['预测值'])):
    plt.text(current, i - width/2, f" {current:,.0f}", va='center', fontsize=9, color='black')
    plt.text(forecast, i + width/2, f" {forecast:,.0f}", va='center', fontsize=9, color='black')

# Add grade labels to the Y axis
for i, level in enumerate(performance_data['等级']):
    plt.text(0, i, f"({level}) ", va='center', ha='right', fontsize=9, color='gray', transform=plt.gca().get_yaxis_transform())

# Set title and labels
plt.xlabel(f'{target_col}')
plt.ylabel(f'{group_col}')
plt.title(f'各{group_col}当前与预测{target_col}对比', fontsize=14, fontweight='bold')
plt.yticks(x_pos, performance_data[group_col])
plt.legend()
plt.grid(axis='x', linestyle='--', alpha=0.5)

# Adjust layout and display
plt.tight_layout()
plt.show()
```
