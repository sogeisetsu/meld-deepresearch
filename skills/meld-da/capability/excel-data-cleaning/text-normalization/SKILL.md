---
name: text-normalization-and-large-file-processing
description: "Standardize and clean text in Excel files (e.g. strip stray prefixes, extract pure CJK characters), then output the cleaned Excel file and report its path."
---

## Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Identify and clean anomalous numeric fields containing prefix symbols, converting them uniformly to integers; also regex-clean text fields, keeping only CJK characters in the Unicode range.
```python
import re
import numpy as np

target_numeric_col = '需要转数字的文本列' # Example: '获赞'
target_text_col = '需要提取中文的列' # Example: '收货人'

# 1. Clean numeric fields that carry prefix symbols
prefix_patterns = ['.', 'I ', '■ ', '一 ', '_', '. ']
def clean_numeric_with_prefix(value):
    val_str = str(value).strip()
    if val_str in ['None', 'nan', '', 'nan']:
        return np.nan
    for prefix in prefix_patterns:
        if val_str.startswith(prefix):
            val_str = val_str[len(prefix):].strip()
            break
    if val_str == '':
        return np.nan
    try:
        return int(val_str)
    except ValueError:
        return np.nan

# 2. Clean text fields, keeping only CJK characters in the Unicode range (\u4e00-\u9fff)
def clean_chinese_name(name):
    if pd.isna(name):
        return name
    s = str(name)
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', s)
    cleaned = ''.join(chinese_chars)
    return cleaned if cleaned else ''

if target_numeric_col in df.columns:
    df[f'{target_numeric_col}_清洗后'] = df[target_numeric_col].apply(clean_numeric_with_prefix)
    
if target_text_col in df.columns:
    df[f'{target_text_col}_清洗后'] = df[target_text_col].apply(clean_chinese_name)
```

Step2 Save the cleaned result as an Excel file, report its plain output path, and free memory to handle the pressure of large-file processing.
```python
output_path = 'normalized_cleaned_result.xlsx'

# Save the cleaned result
df.to_excel(output_path, index=False, engine='openpyxl')
print(f'清洗结果已保存到: {output_path}')

# Report the plain output path
print(f'Output file: {output_path}')

# Free memory
if 'df' in locals():
    del df
    gc.collect()
```
