---
name: condition-filtering-and-large-file-optimization
description: "Choose the processing strategy dynamically by data scale."
---

# condition_filtering

> **Note**: This sub-skill covers one step of the Excel analysis workflow. For the full pipeline (file reading, row counting, large-file optimization, export), see the parent workflow SKILL.md.

Step1 Run multi-dimensional data cleaning and condition filtering, including automatic column-name recognition, RGB color filtering, prefix matching and regex extraction.
```python
# 1. Auto-detect synonymous column names and keep non-null rows
target_cols = ['域名', '缩写', 'code', 'domain']
for col in target_cols:
    if col in df.columns:
        df = df[df[col].notna()]
        break

# 2. Precise filtering on numeric channels (e.g. RGB color filtering)
# Tip: combine multiple conditions with the & operator
if all(c in df.columns for c in ['Red', 'Green', 'Blue']):
    df = df[(df['Red'] == 0) & (df['Green'] == 0) & (df['Blue'] == 0)]

# 3. Filter on string prefixes and convert to numbers for computation
if '编号' in df.columns:
    # Keep only items with a specific prefix
    df = df[df['编号'].astype(str).str.startswith('TXL3')]
    # Tip: use errors='coerce' to tolerate dirty data that cannot convert
    df['val_a'] = pd.to_numeric(df['技工'], errors='coerce')
    df['val_b'] = pd.to_numeric(df['普工'], errors='coerce')
    df['total_val'] = df['val_a'] + df['val_b']
    avg_val = df['total_val'].mean()

# 4. Filter and compute on a specific category value
if '钢筋级别' in df.columns:
    sub_df = df[df['钢筋级别'] == 'Ⅱ'].copy()
    sub_df['target_val'] = pd.to_numeric(sub_df['屈服荷载'], errors='coerce')
    avg_target = sub_df['target_val'].mean()

# 5. Regex matching to extract specific fields
if '命令' in df.columns:
    pattern = r'--pct-'
    matched_df = df[df['命令'].astype(str).str.contains(pattern, na=False)]
    # Keep the key columns for traceability
    extracted_data = matched_df[['NO', '命令', '说明']].copy()
```

Step2 Save the processed result to Excel, style the output file (e.g. whole rows in red), and report its plain output path.
```python
from openpyxl.styles import PatternFill

output_path = "filtered_result.xlsx"

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    if 'total_val' in df.columns:
        df.to_excel(writer, sheet_name='统计结果', index=False)
    if 'extracted_data' in locals():
        extracted_data.to_excel(writer, sheet_name='正则提取', index=False)

# Tip: post-process the styling with openpyxl to highlight key results
wb = openpyxl.load_workbook(output_path)
red_fill = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows(min_row=2):  # Skip the header row
        for cell in row:
            cell.fill = red_fill

wb.save(output_path)

# Report the plain output path
print(f"Result file: {output_path}")
```
