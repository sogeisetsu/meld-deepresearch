---
name: top-value-coloring
description: "Choose the processing strategy dynamically by data scale, merge multi-table data, filter statistically, and use openpyxl to auto-highlight key metrics with styles and export a formatted file."
---

Step1 Extract and merge key-dimension data from multiple sheets, clean the data, convert types, and filter Top-N.
```python
# Example: merge data from two sheets
# Read Sheet1 and clean it
df1 = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
# Assume group_col is in column 0 and value_col in column 2
data1 = df1.iloc[20:, [0, 2]].copy()
data1.columns = ['group_col', 'value_col_1']
data1['value_col_1'] = pd.to_numeric(data1['value_col_1'], errors='coerce')
data1['group_col'] = data1['group_col'].ffill() # Handle missing values caused by merged cells

# Read Sheet2 and clean it
df2 = pd.read_excel(file_path, sheet_name='Sheet2', header=None)
data2 = df2.iloc[5:, [0, 1]].copy()
data2.columns = ['value_col_2', 'value_col_3']

# Merge the data
merged_df = pd.concat([data1.reset_index(drop=True), data2.reset_index(drop=True)], axis=1)
merged_df = merged_df.dropna(subset=['value_col_1'])

# Keep the top five rows for the key metric
top_results = merged_df.nlargest(5, 'value_col_1').copy()

# Placeholder example: fix specific missing values
# top_results.loc[top_results['group_col'].isna(), 'group_col'] = 'Default_Value'
```

Step2 Create a formatted table with openpyxl, apply conditional styles (e.g. red for a specific column, highlight the maximum), and set borders and alignment.
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

output_path = 'analysis_report.xlsx'

# Create the workbook
wb = Workbook()
ws = wb.active
ws.title = 'Analysis_Results'

# Define the styles
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
header_font = Font(bold=True, color='FFFFFF', size=12)
red_font = Font(color='FF0000', bold=True) # Used to highlight anomalous or key values
green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid') # Used to highlight the maximum
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                     top=Side(style='thin'), bottom=Side(style='thin'))
center_align = Alignment(horizontal='center', vertical='center')

# Write the header row
headers = ['Rank'] + list(top_results.columns)
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border

# Write the data and apply styles
for idx, (_, row) in enumerate(top_results.iterrows(), 2):
    # Write the rank
    ws.cell(row=idx, column=1, value=idx-1).border = thin_border
    
    # Write each column's data
    for col_idx, value in enumerate(row, 2):
        cell = ws.cell(row=idx, column=col_idx, value=value)
        cell.border = thin_border
        
        # Conditional highlight example: apply red font to a specific column (e.g. column 4)
        if col_idx == 4:
            cell.font = red_font
        
        # Conditional highlight example: apply green fill to values above a threshold
        # if isinstance(value, (int, float)) and value > threshold_val:
        #     cell.fill = green_fill

# Auto-adjust column widths
column_widths = {'A': 8, 'B': 30, 'C': 15, 'D': 15, 'E': 18}
for col, width in column_widths.items():
    ws.column_dimensions[col].width = width

# Set number formats
for row in range(2, ws.max_row + 1):
    ws.cell(row=row, column=3).number_format = '#,##0'
    ws.cell(row=row, column=4).number_format = '#,##0.00'

wb.save(output_path)
print(f"Formatted file saved to: {output_path}")
```

Step3 Report the plain path of the result file (next to the user's data or in the run's output directory).
```python
# Report the plain output path; no sandbox download link
print(f"Analysis results saved to: {output_path}")
```
