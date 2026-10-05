---
name: invalid-data-cleaning
description: "Preprocess large Excel data: count total rows to decide whether to convert to Parquet for I/O efficiency, regex-clean specific text columns (e.g. keep only CJK characters), then export the cleaned file and report its output path."
---

# Invalid_Data_Cleaning

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

## Skill Steps

Step1 Decide from the total row count whether the data is too large; if so, convert the Excel file to Parquet for faster I/O, then read the data for further analysis.
```python
import pandas as pd

file_path = "input_data.xlsx"
parquet_path = "temp_data.parquet"

# Read the Excel file and convert it to Parquet
xls = pd.ExcelFile(file_path)
dfs = []
for sheet in xls.sheet_names:
    df_sheet = pd.read_excel(xls, sheet_name=sheet)
    dfs.append(df_sheet)

# Concatenate all sheets and write the Parquet file
if dfs:
    df_all = pd.concat(dfs, ignore_index=True)
    df_all.to_parquet(parquet_path, engine='pyarrow', index=False)

# Read the Parquet file for further processing
df = pd.read_parquet(parquet_path)
```

Step2 Clean special characters (such as #, -, digits) in the target text field, using a regex to keep only CJK characters.
```python
import pandas as pd
import re

target_col = 'target_column' # Replace with the column you need to clean

# Define the cleaning function
def clean_chinese_text(text):
    if pd.isna(text):
        return text
    s = str(text)
    # Extract all CJK characters (Unicode range: [一-鿿])
    chinese_chars = re.findall(r'[一-鿿]', s)
    cleaned = ''.join(chinese_chars)
    return cleaned if cleaned else ''

# Apply the cleaning function
if target_col in df.columns:
    df[target_col] = df[target_col].apply(clean_chinese_text)
```

Step3 Save the cleaned data as a spreadsheet file (.xlsx) and report its local output path.
```python
import pandas as pd

# Save the cleaned data as an .xlsx file
output_path = "cleaned_data.xlsx"
df.to_excel(output_path, index=False)

print("清洗后的数据已保存至:", output_path)
# Report the local file path
print("下载链接:", f"file://{output_path}")
```
