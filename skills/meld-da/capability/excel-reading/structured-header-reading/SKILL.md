---
name: excel-large-file-processing-and-cleaning
description: "Read a multi-sheet Excel file, dynamically detect target columns for statistics, regex-clean text fields to extract CJK characters, and finally output a standardized Excel file."
---

# Skill Steps

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Clean text fields with a regular expression to extract pure CJK characters (filtering digits, special symbols, etc.).
```python
import re

def extract_chinese(text):
    if pd.isna(text):
        return text
    # Keep only the Unicode CJK character range
    chinese_chars = re.findall(r'[一-龥]', str(text))
    cleaned = ''.join(chinese_chars)
    return cleaned if cleaned else ''

clean_col = '目标清洗列' # Placeholder example, e.g. '收货人'
if clean_col in df.columns:
    df[clean_col] = df[clean_col].apply(extract_chinese)
```

Step2 Fuzzily match column names dynamically and count specific values in that column.
```python
# Dynamically find the column containing a specific keyword
keyword = 'type'
target_val = 'varchar'
target_col = next((col for col in df.columns if keyword in str(col).lower()), None)

total_target_count = 0
details = []

if target_col is not None:
    # Match case-insensitively, ignoring surrounding spaces
    mask = df[target_col].astype(str).str.lower().str.strip() == target_val
    count = mask.sum()
    total_target_count += count
    
    if count > 0:
        details.append({
            'sheet': target_sheet,
            'target_count': count,
            'total_rows': len(df)
        })

print(f"{'='*50}")
print(f"匹配列 '{target_col}' 中值为 '{target_val}' 的总数: {total_target_count}")
print(f"{'='*50}")
for detail in details:
    print(f"  {detail['sheet']}: {detail['target_count']} 个匹配项 (共 {detail['total_rows']} 行)")
```

Step3 Save the cleaned and processed data as Excel, and report the file size and output path.
```python
output_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), "cleaned_data_output.xlsx")
df.to_excel(output_path, index=False)

file_size = os.path.getsize(output_path)
print(f"清洗后的数据已保存至: {output_path}")
print(f"文件大小: {file_size} 字节")
# Report the plain output path
print(f"下载链接: {output_path}")
```
