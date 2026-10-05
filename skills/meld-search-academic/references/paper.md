# paper.py unified paper-reading entry point

`paper.py` aggregates the paper-reading scripts in the `meld-search-academic/scripts` directory, selects a provider by paper source, and outputs one unified JSON.

It only aggregates paper full-text / section reading; it does not include `search` or `refTree`.

## Basic usage

Read an arXiv paper's full text; the default source is `arxiv`:

```bash
python3 scripts/paper.py 2603.00729
```

Read a specific section of an arXiv paper:

```bash
python3 scripts/paper.py 2603.00729 \
  --section introduction
```

List the available sections of an arXiv paper:

```bash
python3 scripts/paper.py 2603.00729 \
  --list_section
```

Read a PMC paper's full text:

```bash
python3 scripts/paper.py PMC11119143 \
  --source pmc
```

Read a specific section of a PMC paper:

```bash
python3 scripts/paper.py PMC11119143 \
  --source pmc \
  --section methods
```

Write to a JSON file:

```bash
python3 scripts/paper.py 2603.00729 \
  --output results/paper.json
```

## Arguments

| Argument | Description | Default |
| --- | --- | --- |
| `id` | Paper ID, required positional argument. arXiv accepts the raw ID, the `arXiv:` prefix, abs/pdf URLs; PMC accepts `PMC11119143`, `11119143`, PMC URLs | none |
| `--source` | Paper source; supports `arxiv`, `pmc` | `arxiv` |
| `--section`, `-s` | Section name to read; omit to return the full text. Only providers that support section reading receive this argument | none |
| `--list_section` | List the paper's available sections without returning the body; the alias `--list-section` is also supported. Cannot be combined with `--section` | false |
| `--output`, `-o` | Write the final JSON result to the given file; parent directories are created automatically | none |

## Provider fallback chain

Providers within the same source are tried in order. When reading full text/sections, until some provider successfully returns non-empty `content`; when listing sections, until some provider successfully returns non-empty `sections`.

### arxiv

1. `arxiv_paper.py` -> `arxiv_html`
2. `deepxiv_paper.py` -> `deepxiv`
3. `arxiv_pdf_paper.py` -> `arxiv_pdf`

Note: `arxiv_pdf_paper.py` does not support `section` or `list_section`. If `paper.py` is called with `--section` or `--list_section`, the arXiv fallback chain skips `arxiv_pdf`.

### pmc

1. `pmc_paper.py` -> `pmc`

## Parameter dispatch rules

The unified entry point only passes arguments that an internal script supports to the corresponding provider, to avoid script errors caused by extra arguments.

- `id`
  - The arXiv source normalizes it to an arXiv ID before passing it to the arXiv provider
  - The PMC source normalizes it to the numeric ID without the `PMC` prefix before passing it to `pmc_paper.py`
- `section`
  - `arxiv_paper.py`: passed to `cmd_read_section(arxiv_id, section)`
  - `deepxiv_paper.py`: passed to `cmd_read_section(arxiv_id, section)`
  - `pmc_paper.py`: passed to `cmd_read_section(pmc_num, section)`
  - `arxiv_pdf_paper.py`: not passed; skipped directly when `section` is present
- `list_section`
  - `arxiv_paper.py`: calls `cmd_list_sections(arxiv_id)`
  - `deepxiv_paper.py`: calls `cmd_list_sections(arxiv_id)`
  - `pmc_paper.py`: calls `cmd_list_sections(pmc_num)`
  - `arxiv_pdf_paper.py`: not called; skipped directly when `list_section` is present

## Output format

The CLI stdout uses one unified JSON. On success it contains at least:

```json
{
  "success": true,
  "arxiv_id": "2603.00729",
  "source": "arxiv",
  "provider": "arxiv_html",
  "provider_rating": null,
  "content": "<full text / section content>",
  "attempts": [
    {
      "provider": "arxiv_html",
      "success": true,
      "error": null
    }
  ],
  "error": null
}
```

The `pmc` source returns `pmc_id`:

```json
{
  "success": true,
  "pmc_id": "PMC11119143",
  "source": "pmc",
  "provider": "pmc",
  "provider_rating": null,
  "content": "<full text / section content>",
  "error": null
}
```

If `--section` is passed, the output contains a `section` field; if it is not passed, the field is absent.

If `--list_section` is passed, the output contains `sections` and `section_count`, and does not contain `content`:

```json
{
  "success": true,
  "arxiv_id": "2603.00729",
  "source": "arxiv",
  "provider": "arxiv_html",
  "provider_rating": null,
  "section_count": 2,
  "sections": [
    {
      "name": "Abstract",
      "level": 0
    },
    {
      "name": "1 Introduction",
      "level": 1
    }
  ],
  "error": null
}
```

If `--output` is passed, stdout and the file use the same JSON, and the output additionally contains `output_path`:

```json
{
  "success": true,
  "arxiv_id": "2603.00729",
  "source": "arxiv",
  "provider": "arxiv_html",
  "provider_rating": null,
  "content": "<full text / section content>",
  "output_path": "/absolute/path/to/results/paper.json",
  "error": null
}
```

On failure it returns one unified error object and keeps each provider's attempt results:

```json
{
  "success": false,
  "arxiv_id": "2603.00729",
  "source": "arxiv",
  "provider": null,
  "provider_rating": null,
  "content": null,
  "attempts": [
    {
      "provider": "arxiv_html",
      "success": false,
      "error": "HTML unavailable"
    },
    {
      "provider": "deepxiv",
      "success": false,
      "error": "provider returned no content"
    }
  ],
  "error": "arxiv_html: HTML unavailable; deepxiv: provider returned no content"
}
```

## Preserved fields

Besides the unified fields, `paper.py` preserves useful fields returned by the provider, so they are easy for a model to read and to process afterwards.

Common fields include:

- arXiv: `title`, `abs_url`, `html_url`, `pdf_url`, `char_count`, `section_count`, `sections`, `level`, `page_count`
- DeepXiv: `abs_url`, `char_count`
- PMC: `title`, `pmid`, `pmc_url`, `char_count`, `section_count`, `sections`, `level`

## Python API

You can also import and call it directly:

```python
from paper import read_paper

result = read_paper("2603.00729", source="arxiv")
section = read_paper("2603.00729", source="arxiv", section="introduction")
sections = read_paper("2603.00729", source="arxiv", list_section=True)
pmc = read_paper("PMC11119143", source="pmc")
```

The return value has the same structure as the CLI stdout JSON.

## When to use

- First search papers with `search.py` to get an `arxiv_id` or `pmc_id`
- Use `--list_section` first to see the available sections
- Use `paper.py` with defaults to read the full text for overall understanding
- Use `--section` to read key sections in depth, such as `introduction`, `method`, `experiment`, `conclusion`
- When arXiv HTML is unavailable, it automatically falls back to DeepXiv, then to PDF full-text parsing
