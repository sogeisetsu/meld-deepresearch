---
name: category-filtering-and-difficulty-analysis
description: "Run custom category statistics, cross-tab analysis and visualization on Excel data, and compute composite scores and grades from multi-dimensional indicators (text length, term density, regex match, etc.), suited to multi-category distribution statistics and text difficulty/quality assessment."
---

## Skill Steps

### Step1 Load data and configure the environment
```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# Configure a Chinese font so charts render correctly
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

def load_excel_data(file_path: str, skip_rows: int = 2):
    """Read and load data from an Excel file, skipping header rows to get raw data"""
    # Tip: use df.ffill() and friends to handle merged cells
    df = pd.read_excel(file_path, skiprows=skip_rows)
    return df
```

### Step2 Define the category mapping function skeleton
```python
def categorize_data(item: str) -> str:
    """Map concrete items to broad categories (category mapping function skeleton)"""
    if pd.isna(item):
        return '未知'
    if item in ['类别A1', '类别A2', '类别A3']:
        return '大类A'
    elif item in ['类别B1', '类别B2']:
        return '大类B'
    else:
        return '其他'
```

### Step3 Unified analysis and visualization pipeline (bar, pie, cross-tab)
```python
def analyze_and_visualize(df: pd.DataFrame, category_col: str, group_col: str = None, output_path: str = './', top_n: int = None, custom_categorize=None):
    """Unified analysis and visualization: bar chart, pie chart, stacked cross-analysis bar chart"""
    df_clean = df.copy()
    
    # Apply custom category rules
    if custom_categorize:
        df_clean[f'{category_col}大类'] = df_clean[category_col].apply(custom_categorize)
        analyze_col = f'{category_col}大类'
    else:
        analyze_col = category_col
    
    # value_counts + share statistics
    counts = df_clean[analyze_col].value_counts()
    if top_n:
        counts = counts.head(top_n)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Polish the bar chart
    counts.plot(kind='bar', ax=ax1, color='skyblue', edgecolor='black')
    ax1.set_title(f'{analyze_col}分布（柱状图）', fontsize=14, fontweight='bold')
    ax1.set_xlabel(analyze_col, fontsize=12)
    ax1.set_ylabel('数量', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    for i, v in enumerate(counts.values):
        ax1.text(i, v + 0.05, str(v), ha='center', va='bottom', fontweight='bold')
    
    # Polish the pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(counts)))
    wedges, texts, autotexts = ax2.pie(counts.values, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title(f'{analyze_col}分布（饼图）', fontsize=14, fontweight='bold')
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_path}{analyze_col}_分布图.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Cross analysis (crosstab)
    if group_col and group_col in df_clean.columns:
        cross_table = pd.crosstab(df_clean[group_col], df_clean[analyze_col])
        if top_n:
            cross_table = cross_table.head(top_n)
        plt.figure(figsize=(10, 6))
        cross_table.plot(kind='bar', stacked=True, colormap='viridis')
        plt.title(f'各{group_col}的{analyze_col}分布', fontsize=14, fontweight='bold')
        plt.xlabel(group_col, fontsize=12)
        plt.ylabel('数量', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title=analyze_col, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_path}交叉分析图.png', dpi=300, bbox_inches='tight')
        plt.close()
```

### Step4 Multi-dimensional scoring and grading algorithm structure
```python
def analyze_content_difficulty(content: str) -> tuple:
    """Multi-dimensional scoring/grading structure: composite score from length, terminology, regex match, etc."""
    if not isinstance(content, str):
        return 0, '低'
        
    length = len(content)
    
    # Keyword matching
    technical_terms = ['专业术语A', '专业术语B', '核心概念C']
    tech_count = sum(1 for term in technical_terms if term in content)
    
    # Data cleaning and regex matching (e.g. extract numeric requirements)
    has_numeric = bool(re.search(r'\d+', content))
    
    complex_concepts = ['复杂流程X', '高阶操作Y']
    complex_count = sum(1 for concept in complex_concepts if concept in content)
    
    # Composite score formula
    score = (length / 100) * 30 + (tech_count / 10) * 20 + (1 if has_numeric else 0) * 15 + (complex_count / 5) * 35
    
    # Difficulty/quality grading standard
    if score >= 70:
        level = '高'
    elif score >= 40:
        level = '中'
    else:
        level = '低'
    
    return score, level
```

### Step5 Generate the composite-score analysis charts
```python
def generate_comprehensive_analysis(df: pd.DataFrame, content_col: str, output_path: str = './'):
    """Generate composite-score analysis charts for the target content (horizontal bar, trend chart)"""
    # Filter nulls and reset the index
    target_data = df.dropna(subset=[content_col]).reset_index(drop=True)
    
    scores, levels = zip(*target_data[content_col].apply(analyze_content_difficulty))
    target_data['综合评分'] = scores
    target_data['评级'] = levels
    
    # Rating distribution (horizontal bar)
    level_counts = target_data['评级'].value_counts()
    plt.figure(figsize=(10, 6))
    bars = plt.barh(level_counts.index, level_counts.values, color='skyblue', edgecolor='black')
    plt.title('各评级数量分布（横向条形图）', fontsize=14, fontweight='bold')
    plt.xlabel('数量', fontsize=12)
    plt.ylabel('评级', fontsize=12)
    for bar, count in zip(bars, level_counts.values):
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, str(count), va='center', fontsize=10)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_path}评级分布_横向条形图.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Length vs score trend (scatter)
    plt.figure(figsize=(10, 6))
    plt.scatter(target_data[content_col].str.len(), scores, alpha=0.6, color='green')
    plt.title('内容长度与综合评分趋势图', fontsize=14, fontweight='bold')
    plt.xlabel('内容长度（字符数）', fontsize=12)
    plt.ylabel('综合评分', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_path}长度与评分趋势图.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return target_data
```

### Step6 Run the full analysis pipeline
```python
if __name__ == '__main__':
    file_path = 'input_data.xlsx'
    output_path = './output/'
    
    # 1. Load the data
    df = load_excel_data(file_path, skip_rows=2)
    
    # 2. Category statistics and cross analysis
    analyze_and_visualize(
        df, 
        category_col='目标列A', 
        group_col='分组列B', 
        output_path=output_path, 
        custom_categorize=categorize_data
    )
    
    # 3. Multi-dimensional text scoring and visualization
    content_col = '文本内容列'
    if content_col in df.columns:
        processed_df = generate_comprehensive_analysis(df, content_col=content_col, output_path=output_path)
```
