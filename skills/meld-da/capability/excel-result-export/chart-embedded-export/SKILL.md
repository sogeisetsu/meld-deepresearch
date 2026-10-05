---
name: chart-embedded-export
description: "Extract category distributions from structured data for cleaning and statistics, generating multi-dimensional cross analysis, high-resolution comparison charts and a complete analysis report with its output path, suited to large-file handling and embedded visualization."
---

## Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Run data cleaning, handle merged cells, clean text with a regular expression, and build a category mapping function skeleton.
```python
target_col = '分类字段'
value_col = '数值字段'

# Merged-cell handling (fill down to restore)
df[target_col] = df[target_col].ffill()

# Data cleaning: regex-remove special characters, trim, convert types
df[target_col] = df[target_col].astype(str).str.replace(r'[^\w\s]', '', regex=True).str.strip()
df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
df = df.dropna(subset=[target_col, value_col])

# Category mapping function skeleton
def map_category(val):
    if 'A类特征' in str(val): return 'Category_A'
    elif 'B类特征' in str(val): return 'Category_B'
    return 'Other'

df['Mapped_Category'] = df[target_col].apply(map_category)
```

Step2 Run multi-dimensional statistics and cross analysis, computing category shares and generating a cross table with a total row.
```python
group_col = '分组字段'

# value_counts statistics and share computation
counts = df[group_col].value_counts()
proportions = (counts / counts.sum() * 100).round(2)

# Cross analysis (crosstab), including the total row
cross_analysis = pd.crosstab(df[group_col], df['Mapped_Category'], margins=True, margins_name='总计')

# Multi-dimensional aggregation statistics
stats = df.groupby(group_col)[value_col].agg(['sum', 'mean', 'min', 'max']).round(2)
```

Step3 Run business logic computations (e.g. multi-dimensional scoring and grading), export the result to Excel, and report its output path.
```python
# Multi-dimensional scoring/grading algorithm structure
df['Score'] = df[value_col] * 1.5  # Example computation logic
df['Grade'] = pd.cut(df['Score'], bins=[0, 50, 80, 100], labels=['C', 'B', 'A'])

# Export the structured result
output_excel_path = 'analysis_result.xlsx'
df.to_excel(output_excel_path, index=False)

# Report the plain output path
print(f"分析结果已保存，下载链接：[下载结果数据]({output_excel_path})")
```

Step4 Configure Chinese/English fonts, generate a combined visualization panel of pie, bar, box plot and histogram, and export high-resolution images in two formats.
```python
output_img_path = 'comprehensive_chart.png'

# Chinese/English font configuration and chart polish
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('多维度数据分布综合分析', fontsize=16, fontweight='bold')

# Pie chart: distribution shares
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
axes[0, 0].pie(counts.values, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
axes[0, 0].set_title('分组选项分布比例')

# Bar chart: cross-category distribution
plot_data = cross_analysis.drop('总计', axis=0, errors='ignore').drop('总计', axis=1, errors='ignore')
plot_data.plot(kind='bar', ax=axes[0, 1], color=colors[:len(plot_data.columns)])
axes[0, 1].set_title('不同分组下分类分布')
axes[0, 1].tick_params(axis='x', rotation=45)

# Box plot: numeric distribution
df.boxplot(column=value_col, by=group_col, ax=axes[1, 0])
axes[1, 0].set_title('不同分组下数值分布')

# Histogram: frequency distribution
for grp in df[group_col].dropna().unique():
    subset = df[df[group_col] == grp]
    axes[1, 1].hist(subset[value_col].dropna(), alpha=0.7, label=str(grp), bins=8)
axes[1, 1].legend()
axes[1, 1].set_title('数值分布直方图')

plt.tight_layout()
# High-resolution image export
plt.savefig(output_img_path, format='png', dpi=300)
plt.savefig(output_img_path.replace('.png', '.svg'), format='svg')
plt.close()
```

Step5 Combine the statistics and chart paths into a complete Markdown analysis report with key findings and detailed insights.
```python
report = [
    "# 数据综合分析报告\n",
    "## 1. 关键发现",
    f"- 数据集共包含 {len(df)} 条有效记录。",
]

for idx, val in proportions.items():
    report.append(f"- 分组 '{idx}' 的占比为 {val}%。")

report.extend([
    "\n## 2. 交叉分析汇总",
    cross_analysis.to_markdown(),
    "\n## 3. 聚合统计指标",
    stats.to_markdown(),
    f"\n## 4. 可视化分析\n![综合分析图表]({output_img_path})\n",
    "**结论**: 各类别在数据中呈现特定分布特征，详细明细与评分定级结果请参考上方下载链接获取完整附件。"
])

report_content = '\n'.join(report)
print(report_content)
```
