---
name: excel-multi-sheet-threshold-analysis
description: "Count the total rows of a multi-sheet Excel file and choose the processing strategy by scale, extract specific dimensions for deduplication statistics, and generate summary and detail reports."
---

# Excel_Multi_Sheet_Deduplication

> This sub-skill covers one capability of the Excel workflow. For reading/counting/Parquet optimization, see the parent workflow SKILL.md.

Step1 Load the target data sheet and preview its structure.
```python
import pandas as pd

file_path = 'input_file.xlsx'
target_sheet = 'Sheet1' # Specify the sheet name for your case

# Read the data; header=None handles headerless or non-standard header files
df = pd.read_excel(file_path, sheet_name=target_sheet, header=None)
print(f"数据形状: {df.shape}")
print("前 5 行预览：")
print(df.head())
```

Step2 Walk the data rows, extract target information by keyword, and clean the data (trim spaces, filter nulls).
```python
import pandas as pd

# Set the target column index and filter keywords
target_col_idx = 1 
keywords = ["关键词A", "关键词B"] # Example: e.g. "综合楼", "控制中心"
extracted_data = []

for idx, row in df.iterrows():
    cell_val = str(row[target_col_idx]) if pd.notna(row[target_col_idx]) else ""
    # Clean the data: trim surrounding spaces and match keywords
    clean_val = cell_val.strip()
    if any(k in clean_val for k in keywords):
        if clean_val and clean_val.lower() not in ["nan", "null", ""]:
            extracted_data.append(clean_val)

print(f"提取到相关记录共 {len(extracted_data)} 条")
```

Step3 Deduplicate the extracted information by category and count the unique items per dimension.
```python
# Use a set for efficient deduplication
category_a_items = set()
category_b_items = set()

for item in extracted_data:
    if "关键词A" in item:
        category_a_items.add(item)
    elif "关键词B" in item:
        category_b_items.add(item)

# Convert to sorted lists
list_a = sorted(list(category_a_items))
list_b = sorted(list(category_b_items))

print(f"类别A 唯一项数量: {len(list_a)}")
print(f"类别B 唯一项数量: {len(list_b)}")
```

Step4 Assemble the statistics summary and the detailed list into DataFrames and export them as Excel files, reporting their output paths.
```python
import pandas as pd

# 1. Build the statistics summary
summary_df = pd.DataFrame({
    '分类名称': ['类别A', '类别B'],
    '唯一项总数': [len(list_a), len(list_b)]
})

# 2. Build the detailed list
detail_list = []
for val in list_a:
    detail_list.append({'分类': '类别A', '详细名称': val})
for val in list_b:
    detail_list.append({'分类': '类别B', '详细名称': val})
detail_df = pd.DataFrame(detail_list)

# Export the results
output_summary_path = 'summary_report.xlsx'
output_detail_path = 'detail_list.xlsx'

summary_df.to_excel(output_summary_path, index=False)
detail_df.to_excel(output_detail_path, index=False)

print(f"统计摘要已保存: {output_summary_path}")
print(f"详细清单已保存: {output_detail_path}")
```
