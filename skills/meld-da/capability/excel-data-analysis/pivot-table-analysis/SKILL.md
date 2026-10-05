---
name: pivot-table-cross-analysis
description: "Use cross-tabulation and heatmaps for multi-dimensional share analysis of categorical data, suited to cleaning and visualizing structured data such as award distribution, performance evaluation or market share."
---

Step1 Clean and restructure the raw data, handle missing values caused by Excel merged cells, and select the core analysis columns.
```python
import pandas as pd

def preprocess_pivot_data(file_path, target_cols=['奖项', '项目名称', '成员', '单位']):
    """
    Clean and restructure the data columns, handling merged-cell fills.
    """
    df = pd.read_excel(file_path)
    # Map generic column names
    df.columns = target_cols
    
    # Key trick: handle merged cells. Ensure the data is ordered by the original category order before ffill
    # Assume the first column holds the category labels (e.g. award names)
    df[target_cols[0]] = df[target_cols[0]].fillna(method='ffill')
    
    # Drop invalid rows missing key information (e.g. member or organization)
    df = df.dropna(subset=[target_cols[2], target_cols[3]])
    
    # Trim whitespace in strings
    for col in df.select_dtypes(['object']).columns:
        df[col] = df[col].str.strip()
        
    return df
```

Step2 Build a cross-analysis table (crosstab), computing the frequency distribution and percentage share per dimension.
```python
def create_cross_analysis(df, index_col='单位', columns_col='奖项'):
    """
    Build the cross table and compute the win/distribution ratio per category dimension.
    """
    # Generate the frequency crosstab
    cross_table = pd.crosstab(df[index_col], df[columns_col])
    
    # Compute shares: the distribution of each row (unit) under each column (award)
    # div(axis=1) divides after summing each column
    award_proportions = cross_table.div(cross_table.sum(axis=0), axis=1) * 100
    
    # Trick: build a summary table with a total row and shares
    summary = cross_table.copy()
    summary['总计'] = summary.sum(axis=1)
    summary.loc['合计'] = summary.sum()
    
    return cross_table, award_proportions, summary
```

Step3 Configure a Chinese font and generate a heatmap visualization that shows the distribution differences across dimensions.
```python
import matplotlib.pyplot as plt
import seaborn as sns

def generate_analysis_heatmap(proportions, output_path='analysis_heatmap.png'):
    """
    Generate a high-resolution heatmap with Chinese font support.
    """
    # Key trick: Chinese font configuration that works across systems
    plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    plt.figure(figsize=(14, 10))
    
    # Draw the heatmap with Seaborn; fmt='.2f' keeps two decimals
    sns.heatmap(
        proportions, 
        annot=True, 
        fmt='.2f', 
        cmap='YlGnBu', 
        linewidths=.5,
        cbar_kws={'label': '占比 (%)'}
    )
    
    plt.title('多维度分类占比分布热力图', fontsize=15, pad=20)
    plt.xlabel('分类维度 (Columns)', fontsize=12)
    plt.ylabel('分析对象 (Index)', fontsize=12)
    
    # Auto-adjust the layout so labels are not clipped
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

Step4 Run the combined analysis to extract the Top-N performers per dimension and compute the overall ranking.
```python
def extract_performance_insights(proportions, top_n=3):
    """
    Find the leaders under each award/category and compute overall weighted performance.
    """
    insights = {}
    
    # 1. Extract the top N for each category dimension
    top_performers = {}
    for category in proportions.columns:
        top_list = proportions[category].sort_values(ascending=False).head(top_n)
        top_performers[category] = top_list.to_dict()
    
    # 2. Compute the overall performance ranking (mean share across all dimensions)
    overall_performance = proportions.mean(axis=1).sort_values(ascending=False)
    
    insights['top_by_category'] = top_performers
    insights['overall_ranking'] = overall_performance.head(10).to_dict()
    
    return insights
```

Step5 Export the analysis results as a multi-sheet Excel file and provide a link to it.
```python
from IPython.display import FileLink

def export_results(cross_table, proportions, insights_df, file_name='analysis_report.xlsx'):
    """
    Save the analysis results to Excel and return a link in the environment.
    """
    with pd.ExcelWriter(file_name) as writer:
        cross_table.to_excel(writer, sheet_name='频数统计')
        proportions.to_excel(writer, sheet_name='占比分析')
        insights_df.to_excel(writer, sheet_name='综合排名')
    
    return FileLink(file_name)
```
