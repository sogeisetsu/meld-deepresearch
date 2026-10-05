---
name: excel-smart-analysis-and-cleaning
description: "Smart cleaning, cross-sheet reconciliation and visualization analysis for multi-sheet Excel files."
---

Step1 Deep-clean the data, including merged-cell forward fill (ffill), regex text processing, RGB color-component conversion, and outlier identification.
```python
import re

def clean_data(df, target_col):
    # 1. Handle merged cells: fill down
    df[target_col] = df[target_col].ffill()
    
    # 2. Regex cleaning: strip numeric prefixes, special characters and surrounding spaces
    def regex_clean(text):
        if not isinstance(text, str): return text
        text = re.sub(r'^\d+[\.\s\-]+', '', text) # Remove prefixes like "1. "
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text) # Keep only CJK, Latin and digits
        return text.strip()
    
    df[target_col] = df[target_col].apply(regex_clean)
    
    # 3. Numeric conversion and RGB-based filtering (example: keep black/colorless values)
    # Assume the column names are 'Red', 'Green', 'Blue'
    rgb_cols = ['Red', 'Green', 'Blue']
    for col in rgb_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if all(c in df.columns for c in rgb_cols):
        black_mask = (df['Red'] == 0) & (df['Green'] == 0) & (df['Blue'] == 0)
        df = df[black_mask]
        
    return df

# Walk all sheets and clean them
cleaned_dfs = {name: clean_data(df, 'group_col') for name, df in df_dict.items()}
```

Step2 Run cross-sheet reconciliation and multi-dimensional statistics (e.g. cross-tabulation, share statistics), and identify key metrics (e.g. issue discovery rate).
```python
# Cross-sheet reconciliation example: compare the value totals of Sheet1 and Sheet2
if 'Sheet1' in cleaned_dfs and 'Sheet2' in cleaned_dfs:
    val1 = cleaned_dfs['Sheet1']['amount'].sum()
    val2 = cleaned_dfs['Sheet2']['amount'].sum()
    print(f"核对结果: Sheet1({val1}) vs Sheet2({val2}), 差异: {val1 - val2}")

# Cross-tabulation and share statistics
target_df = pd.concat(cleaned_dfs.values(), ignore_index=True)
pivot_table = pd.crosstab(target_df['category_col'], target_df['status_col'])
pivot_table['占比'] = pivot_table.sum(axis=1) / pivot_table.sum().sum()

# Compute the maximum under a specific condition (e.g. max dosage in a mix design)
# df.groupby('id_col')['value_col'].max()
```

Step3 Generate visualization charts with Chinese/English font support, and output a styled Excel result with its output path.
```python
import matplotlib.pyplot as plt
from openpyxl.styles import Font

# 1. Visualization configuration
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans'] # Chinese support
plt.rcParams['axes.unicode_minus'] = False

plt.figure(figsize=(10, 6), dpi=100)
target_df['category_col'].value_counts().plot(kind='bar', color='skyblue')
plt.title("数据分布统计")
plt.tight_layout()
plt.savefig("analysis_chart.png")

# 2. Styled output
output_path = "analysis_result.xlsx"
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    target_df.to_excel(writer, index=False, sheet_name='Result')
    
    # Mark specific cells red and bold (e.g. anomalous values)
    workbook = writer.book
    worksheet = writer.sheets['Result']
    red_bold_font = Font(color="FF0000", bold=True)
    
    for row in range(2, worksheet.max_row + 1):
        # Assume column 3 is the numeric column to check
        if worksheet.cell(row=row, column=3).value > 100:
            worksheet.cell(row=row, column=1).font = red_bold_font

print(f"分析完成，结果已保存至: {output_path}")
# Report the plain output path (environment-dependent)
# print(f"Download link: [download]({output_path})")
```
