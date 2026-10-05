---
name: excel-data-analysis-and-report-generation
description: "Extract multiple data types from Excel and generate a comprehensive analysis report with visualization charts and its output path."
---

## Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Extract valid codes or apply category mapping on specified columns, build a statistics table with shares and a total row, and support cross analysis.
```python
# Category mapping function skeleton
def categorize_item(item_name):
    category_a_keywords = ['keyword1', 'keyword2'] # Placeholder example
    if pd.isna(item_name):
        return '未知'
    if any(kw in str(item_name) for kw in category_a_keywords):
        return '类别A'
    return '其他'

target_col = '项目名称' # Replace with your actual column name
group_col = '所属区域'  # Replace with your actual group column name

if target_col in combined_df.columns:
    combined_df['分类'] = combined_df[target_col].apply(categorize_item)
    
    # value_counts + share + total row
    category_counts = combined_df['分类'].value_counts().reset_index()
    category_counts.columns = ['类别', '数量']
    total = category_counts['数量'].sum()
    category_counts['占比'] = (category_counts['数量'] / total).apply(lambda x: f'{x:.2%}')
    
    total_row = pd.DataFrame([{'类别': '总计', '数量': total, '占比': '100.00%'}])
    category_counts = pd.concat([category_counts, total_row], ignore_index=True)
    
    # Cross analysis crosstab
    if group_col in combined_df.columns:
        cross_tb = pd.crosstab(combined_df[group_col], combined_df['分类'], margins=True, margins_name='总计')
        print("交叉分析结果:\n", cross_tb)
```

Step2 Identify rows whose target value exceeds the limit, locating by keyword and searching backwards for the limit to keep the data associated.
```python
import re

exceed_rows = []
df_target = combined_df.copy()

for i, row in df_target.iterrows():
    if '共计' in str(row.iloc[0]):
        try:
            target_val = float(row.iloc[8]) # Column index of the target value
        except (ValueError, TypeError):
            continue
        
        limit_val = None
        structure_name = "未知结构"
        
        # Search backwards for the limit
        for j in range(i-1, max(0, i-15), -1):
            check_row = df_target.iloc[j, :]
            check_str = ' '.join([str(x) for x in check_row.values if pd.notna(x)])
            if '限值' in check_str:
                # Data cleaning regex
                match = re.search(r'限值([\d.]+)', check_str)
                if match:
                    limit_val = float(match.group(1))
                    for k in range(j-1, max(0, j-5), -1):
                        name_row = df_target.iloc[k, 0]
                        if pd.notna(name_row) and '关键字' in str(name_row):
                            structure_name = str(name_row)
                            break
                    break
        
        # Multi-dimensional scoring/grading algorithm structure
        if limit_val is not None and target_val > limit_val:
            severity = '高' if (target_val - limit_val) > 10 else '中'
            exceed_rows.append({
                'row_index': i,
                'structure_name': structure_name,
                'target_val': target_val,
                'limit': limit_val,
                'exceed_value': target_val - limit_val,
                'severity': severity
            })
```

Step3 Generate a high-resolution visualization of category shares, save the statistics, and report the output paths.
```python
import matplotlib.pyplot as plt
import matplotlib

# Chinese/English font configuration
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# Prepare the chart data (exclude the total row)
plot_data = category_counts[category_counts['类别'] != '总计']
categories = plot_data['类别'].tolist()
counts = plot_data['数量'].tolist()

# Chart polish (dpi, color scheme, label positions)
fig, ax = plt.subplots(figsize=(10, 8))
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#F9A826']
explode = [0.05] * len(categories)

wedges, texts, autotexts = ax.pie(
    counts, 
    labels=categories, 
    autopct='%1.1f%%',
    startangle=90,
    colors=colors[:len(categories)],
    explode=explode,
    shadow=True,
    textprops={'fontsize': 12}
)

ax.set_title('各类别数量占比分析', fontsize=16, fontweight='bold', pad=20)
ax.legend(wedges, categories, title="类别", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

# Save the chart
chart_path = os.path.join(output_dir, 'category_analysis.png')
plt.savefig(chart_path, dpi=150, bbox_inches='tight')

# Save the statistics and report the paths
output_path = os.path.join(output_dir, 'analysis_result.xlsx')
category_counts.to_excel(output_path, index=False)

print(f"统计结果已保存至: {output_path}")
print(f"下载链接: [下载统计结果]({output_path})")
print(f"图表下载链接: [下载图表]({chart_path})")
```
