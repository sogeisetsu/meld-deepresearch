---
name: meld-da
description: "Excel / spreadsheet data analysis workflow. Orchestrates a full pipeline: (1) count rows across all sheets, (2) large-file detection with Parquet caching for 10k+ rows, (3) data cleaning (missing values, text normalization, invalid characters), (4) condition and category filtering, (5) cross-sheet aggregation and statistics, (6) export to Excel/CSV. Use this skill proactively - do not answer with a few pandas lines - whenever any of these hold: (a) trigger words like Excel analysis, spreadsheet analysis, data analysis, data cleaning, statistics, filtering, visualization, data export, pivot table, group-by, trend analysis, comparison analysis, outlier detection, deduplication, missing-value handling; (b) the user shares a .xlsx/.xls/.csv file and asks for analysis, cleaning, statistics or visualization; (c) the analysis involves multi-sheet reading, filtering, aggregation or chart generation; (d) the user wants a formatted Excel report exported. Not for plain text, image analysis, or single-formula questions."
license: MIT
metadata:
  author: sogeisetsu
  repository: https://github.com/sogeisetsu/meld-deepresearch
  version: "0.4.0"
---

# Excel Data Analysis Workflow

End-to-end workflow for structured Excel analysis. Each step maps to a
capability sub-skill that can be loaded for detailed patterns.

## Dependencies and fallback

The example code in this skill needs the third-party packages listed in this
directory's `requirements.txt` (pandas, openpyxl, pyarrow, and the charting
stack). They are **optional for the host**: install them only when the
analysis actually runs, and never install them from inside a script.

When a package or the package index is unavailable, **degrade instead of
failing**:

1. Read and inspect the tables with the zero-dependency layer
   `skills/meld-deepresearch/scripts/read_table.py` (Python stdlib only) —
   row counts, sheet inventory, header and sample values are all reachable
   that way.
2. Continue the workflow steps that need no third-party package (row counting
   with `openpyxl` is itself part of `requirements.txt`, so use `read_table.py`
   when it is missing), and mark the analysis steps you could not run as gaps.
3. Tell the user which steps were skipped and why — never deliver a
   statistics or chart section whose numbers were not actually computed.

`read_table.py` inspects and extracts; this skill analyses. The two are
complementary, and neither replaces the other.

## Hand-off entry & exit

- **Entry:** this skill works standalone, and may also be handed off to from
  `skills/meld-deepresearch` as documented in that skill's
  `references/protocol.md` §2a — local table files plus the analysis of them
  come to `meld-da`.
- **Exit:** when invoked as a hand-off, return reproducible numbers/quotes
  plus the exact re-runnable command, so the caller can record them as
  `observations[]`/`sources[]`; never write into the caller's evidence files.
  If a dependency or the sibling skill is missing, degrade and say so instead
  of failing.

## Workflow

### Step 1 — Count rows across all sheets (lightweight, no full load)

Count rows per sheet **without loading data into memory**. Use openpyxl
`read_only` mode — this works for any file size.

```python
import openpyxl, gc

wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
total_rows = 0
sheet_info = {}
for name in wb.sheetnames:
    ws = wb[name]
    row_count = sum(1 for _ in ws.iter_rows(min_row=2, values_only=True))
    total_rows += row_count
    sheet_info[name] = row_count
    print(f"Sheet '{name}': {row_count} rows")
wb.close()
print(f"总行数={total_rows}")
```

⚠️ **Do NOT use `pd.read_excel()` to count rows** — it loads all data into
memory, which will OOM on large files.

→ capability: `excel-reading/multi-sheet-reading`

### Step 2 — Large file gate (CRITICAL — choose strategy by row count)

| total_rows | Strategy | What to do |
|-----------|----------|------------|
| < 10k | Direct read | `df = pd.read_excel(file_path, sheet_name=target_sheet)` |
| 10k – 100k | Parquet cache | `pd.read_excel()` once → `df.to_parquet()` → all later reads from Parquet |
| **>= 100k** | **STOP. Load the `excel-reading/large-excel-reading` capability** | Read its SKILL.md, then follow its streaming read + Parquet pattern. **Do NOT use `pd.read_excel()` at all** — it will OOM or timeout on 100k+ rows. |

**For >= 100k rows:** open the capability file
`capability/excel-reading/large-excel-reading/SKILL.md` (path is relative to
the directory containing this SKILL.md), then follow its Parquet caching
pattern: read once in openpyxl `iter_rows` chunks (e.g. 50k rows at a time,
constant memory), convert to Parquet, and serve all later reads from Parquet.

**For 10k – 100k rows (only):**
```python
import os, tempfile
import pandas as pd
parquet_path = os.path.join(tempfile.gettempdir(), "_auto_parquet.parquet")
df = pd.read_excel(file_path, sheet_name=target_sheet)
df.to_parquet(parquet_path, engine="pyarrow")
del df; gc.collect()
df = pd.read_parquet(parquet_path)
```

→ capability: `excel-reading/large-excel-reading`

### Step 3 — Inspect schema & data types

Preview target sheet structure. **For large files (>= 10k rows), only read
a small sample — never full load just to inspect.**

```python
# For any file size — read only first N rows for inspection
df_head = pd.read_excel(file_path, sheet_name=target_sheet, nrows=20)
print(f"Columns: {df_head.columns.tolist()}")
print(f"Dtypes:\n{df_head.dtypes}")
print(df_head.head(10))
```

→ capability: `excel-reading/range-reading`

### Step 4 — Data cleaning

Handle missing values, normalize text, clean invalid characters.

```python
# Missing values
null_count = df[col].isna().sum()

# Text cleaning: keep only Chinese characters
import re
def clean_text(val):
    if pd.isna(val): return val
    return "".join(re.findall(r"[\u4e00-\u9fff]", str(val))) or ""

df[col] = df[col].apply(clean_text)
```

⚠️ **Large file rule**: When `total_rows >= 100k`, do NOT use `df.apply(lambda...)`.
Use vectorized operations or `np.where()` instead. See the
`excel-reading/large-excel-reading` capability for the vectorized cheat sheet.

→ capabilities:
  - `excel-data-cleaning/missing-value-handling`
  - `excel-data-cleaning/invalid-data-cleaning`
  - `excel-data-cleaning/text-normalization`

### Step 5 — Filter & extract

Apply condition or category filters, aggregate results.

```python
# Condition filter
mask = df[col].astype(str).str.strip() == target_value
filtered = df[mask]

# Category extraction (for headerless layouts)
df_raw = pd.read_excel(file_path, sheet_name=sheet, header=None)
# Walk rows to find category markers, collect items until next marker
```

→ capabilities:
  - `excel-data-filtering/condition-filtering`
  - `excel-data-filtering/category-filtering`
  - `excel-data-filtering/threshold-filtering`

### Step 6 — Export results

Save filtered/cleaned data as Excel or CSV, next to the user's data file (or
in the run's output directory). Report the plain path in your reply.

```python
import os
output_path = os.path.join(os.path.dirname(file_path), "result.xlsx")
result_df.to_excel(output_path, index=False, engine="openpyxl")
print(f"Saved: {output_path}")
```

→ capabilities:
  - `excel-result-export/single-sheet-export`
  - `excel-result-export/formatted-export`

## Key rules

- **Always count rows first** — gate large-file logic on the 10k threshold.
- **>= 100k rows → MUST load the `excel-reading/large-excel-reading`
  capability** — do not attempt to handle with `pd.read_excel()`.
- **Column names may contain spaces** (e.g. `'Pass Status'`) — use exact
  string indexing.
- **Headerless sheets** — use `header=None` and positional indexing.
- **Prohibited on large files (>= 100k rows)**:
  - `pd.read_excel()` for full load (use streaming read → Parquet)
  - `df.apply(lambda...)` or `df.iterrows()` (use vectorized ops or `itertuples()`)
  - `fc-list`, `find ... fonts`, `subprocess` to search fonts, or `pip install` (use fixed font paths below)
  - Printing all unique values or full DataFrames (use `.head()`, `.value_counts().head()`)

## CJK Font Setup (mandatory for charts)

When generating charts with matplotlib, **copy this block as-is**. Do NOT search for fonts.

```python
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

_FONT_PATHS = [
    os.path.expanduser('~/.fonts/SimHei.ttf'),
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/SimHei.ttf',
]
for _p in _FONT_PATHS:
    if os.path.exists(_p):
        fm.fontManager.addfont(_p)
        matplotlib.rcParams['font.family'] = fm.FontProperties(fname=_p).get_name()
        break
matplotlib.rcParams['axes.unicode_minus'] = False
```

If none of the paths exist on this machine, fall back to whatever CJK-capable
font the host already has installed — do not run font-discovery commands.

## How to load sub-skills

Each workflow step references one or more capability sub-skills. When you
need the detailed code pattern for a step, open the sub-skill on demand:

```
capability/{category}/{sub-skill-name}/SKILL.md
```

The path is relative to the directory containing this SKILL.md.

**Rules:**
- Only load the sub-skill(s) needed for your current step.
- Do NOT load all sub-skills at once — it wastes context.
- The top-level workflow (this file) is your guide; sub-skills provide
  detailed implementation patterns.

## Available capability sub-skills

Base path: `capability/{category}/{sub-skill}/SKILL.md` (relative to the
directory containing this SKILL.md).

### excel-reading — Reading and parsing

| Sub-skill | Function |
|---|---|
| single-sheet-reading | Read a single worksheet, with merged-cell handling, cross-tab analysis and multi-dimensional visualization |
| multi-sheet-reading | Read multiple worksheets, enable Parquet optimization dynamically by data volume, with regex cleaning, category aggregation and linear fitting |
| range-reading | Extract data from a specific range, choosing the processing strategy dynamically by data volume |
| large-excel-reading | Handle large Excel files with optional Parquet conversion for speed, and generate formatted reports with conditional highlighting |
| multi-file-reading | Read and aggregate multiple files, with large-file Parquet conversion and visualization reports |
| specific-sheet-reading | Cross-sheet statistics on specific fields, data cleaning and cross-tab analysis, producing a summary report with the output path |
| structured-header-reading | Dynamically identify target columns for statistics, and regex-clean text fields to extract CJK characters |

### excel-data-cleaning — Data cleaning

| Sub-skill | Function |
|---|---|
| missing-value-handling | Smart multi-sheet cleaning, cross-sheet reconciliation and visualization analysis |
| duplicate-removal | Multi-sheet deduplication statistics, producing summary and detail reports |
| invalid-data-cleaning | Regex-clean specific text columns (e.g. keep only CJK characters), with automatic Parquet acceleration for large files |
| text-normalization | Text normalization cleaning (strip stray prefixes, extract pure CJK characters, etc.) |
| numeric-format-normalization | Numeric format normalization, with key-metric total reconciliation and result file export |
| outlier-detection | IQR outlier detection combined with skewness/kurtosis distribution analysis, for preprocessing non-normal data |

### excel-data-filtering — Data filtering

| Sub-skill | Function |
|---|---|
| condition-filtering | Conditional filtering with the processing strategy chosen dynamically by data volume |
| category-filtering | Custom category statistics and cross-tab analysis, with composite scoring and grading by text length / term density / regex match, etc. |
| range-filtering | Filter by multi-dimensional numeric conditions and export, with automatic performance optimization for large data |
| threshold-filtering | Numeric column cleaning and conditional filtering, styling matching cells with openpyxl |

### excel-data-analysis — Data analysis

| Sub-skill | Function |
|---|---|
| comparison-analysis | Compare two groups of categorical data, count differences and ratios, and produce visualizations |
| group-by-analysis | Multi-sheet data cleaning and group-by aggregation, producing styled statistics tables and charts |
| kpi-metric-analysis | Extract key metrics for unit-consistency validation and ranking analysis |
| pivot-table-analysis | Cross-tab tables and heatmaps for multi-dimensional share analysis, suited to award distribution / performance evaluation / market share |
| time-series-analysis | Time-series trend analysis, percentage cleaning, performance grading modeling and forecasting, producing high-resolution visualization reports |
| trend-analysis | Multi-dimensional graded evaluation and trend forecasting with differentiated growth rates, suited to performance evaluation / goal setting |

### excel-data-statistics — Statistical computation

| Sub-skill | Function |
|---|---|
| basic-statistics | Basic statistics: conditional mean over filtered rows, and deduplicated sums over a specified row range, with result files and the output path |
| category-statistics | Count and share per category, producing combined bar chart / pie chart visualization reports |
| grouped-statistics | Merge multi-sheet data with forward fill, then compute grouped statistics |
| percentage-calculation | Extract key metrics by row scan or column matching and compute share / mean, outputting structured reports and charts |

### excel-data-visualization — Data visualization

| Sub-skill | Function |
|---|---|
| bar-chart-visualization | Handle merged cells, cross-group statistics, and draw polished bar charts supporting Chinese and English fonts |
| histogram-visualization | Numeric distribution analysis and outlier detection, with regex extraction of error terms, producing box plots and histograms |
| line-chart-visualization | Feature cleaning and clustering analysis, producing multi-dimensional charts for trend comparison / distribution features / parameter sensitivity |
| pie-chart-visualization | Category summary statistics with automatic key-field detection, producing polished pie charts including shares and values |
| scatter-plot-visualization | Multi-dimensional statistical analysis with scatter plot visualization |
| stacked-chart-visualization | Percentage-string data handling, filling in missing dimensions, producing stacked bar charts that show compositional trends |

### excel-cell-coloring — Cell coloring

| Sub-skill | Function |
|---|---|
| category-coloring | Extract the target metric, compute its maximum, and highlight specific rows |
| duplicate-value-coloring | Compare a specific coefficient across tables and color-mark outliers |
| outlier-coloring | Identify out-of-range values and erroneous cells and highlight them |
| threshold-cell-coloring | Compute time-series averages per dimension and emit conditional formatting with openpyxl (e.g. below-average cells in green) |
| top-value-coloring | Choose the strategy dynamically by data volume: merge multiple tables, filter statistically, and auto-highlight key metrics with styles |

### excel-conditional-formatting — Conditional formatting

| Sub-skill | Function |
|---|---|
| data-bar-formatting | Extract numbers from unit-suffixed string columns and clean them, producing combined histogram / pie / bar / cumulative-distribution charts |

### excel-result-export — Result export

| Sub-skill | Function |
|---|---|
| single-sheet-export | Explore and condition-filter multi-sheet data, rename fields, and export a new Excel file with the output path |
| formatted-export | Filter records by condition and export them as an Excel file with whole rows marked red |
| chart-embedded-export | Clean and summarize category distributions, producing multi-dimensional cross-analysis and high-resolution embedded-chart reports |
| report-generation-export | Extract multiple data types from Excel and produce a comprehensive analysis report with visualizations and the output path |

### excel-table-styling — Table styling

| Sub-skill | Function |
|---|---|
| table-theme-styling | Large-file Parquet-accelerated reads, conditional filtering / category aggregation and result export |

## Platform notes (pure Windows)

- Run scripts with `python` when `python3` is not on `PATH` (on stock Windows
  `python3` may be the Microsoft Store stub). Every command in this skill is
  written as `python3 …`; substituting `python` is the only change needed.
- The scripts use `pathlib.Path` throughout and never assume a POSIX temp
  directory, a POSIX shell or `/` separators, so no other change is required.
- Chart CJK fonts follow this skill's own `## CJK Font Setup` section —
  copy that block as-is instead of searching for fonts.
