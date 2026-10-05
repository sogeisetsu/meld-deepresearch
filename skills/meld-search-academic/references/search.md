# search.py unified academic search entry point

`search.py` aggregates the search scripts in the `meld-search-academic/scripts` directory, calls different providers per logical search source, and outputs one unified JSON.

It only aggregates search functionality; it does not include the `paper`, `pdf_paper`, `refTree`, or other paper-reading / citation-tree scripts.

## Basic usage

```bash
python3 scripts/search.py "NSA"
```

Select search sources:

```bash
python3 scripts/search.py "NSA" \
  --source arxiv,semantic,wikipedia \
  --limit 5
```

Write to a JSON file:

```bash
python3 scripts/search.py "NSA" \
  --source arxiv,semantic \
  --limit 5 \
  --output results/search.json
```

## Arguments

| Argument | Description | Default |
| --- | --- | --- |
| `query` | Search keywords, required positional argument | none |
| `--source`, `--sources`, `-s` | Search sources; comma-separated or repeatable | `all` |
| `--limit`, `-n` | Number of results per source | `10` |
| `--category`, `-c` | ArXiv category filter, only passed to providers that support categories | none |
| `--lang`, `-l` | Language hint, only passed to providers that support `lang` | none |
| `--output`, `-o` | Write the final output JSON to a file; parent directories are created automatically | none |
| `--provider-timeout` | Timeout per provider call in seconds; `0` means no limit | `60` |

Supported `--source` values:

- `all`
- `arxiv`
- `semantic`
- `google_scholar`
- `pubmed`
- `ssrn`
- `wikipedia`

`--source all` is equivalent to:

```text
arxiv,semantic,google_scholar,pubmed,ssrn,wikipedia
```

## Provider fallback chain

### arxiv

Tried in order until some provider successfully returns non-empty results:

1. `arxiv_search.py` -> `arxiv_official`
2. `deepxiv_search.py` -> `deepxiv`
3. `openalex_search.py` -> `openalex`
4. `arxiv_crawler_search.py` -> `arxiv_crawler`
5. `crossref_search.py` -> `crossref`
6. `arxiv_mirror_search.py` -> `arxiv_mirror`

### semantic

Tried in order until some provider successfully returns non-empty results:

1. `semantic_scholar_search.py` -> `semantic_scholar_official`
2. `semantic_scholar_crawler_search.py` -> `semantic_scholar_crawler`

### Standalone sources

- `google_scholar` -> `google_scholar_search.py`
- `pubmed` -> `pubmed_search.py`
- `ssrn` -> `ssrn_search.py`
- `wikipedia` -> `wikipedia_search.py`

## Parameter dispatch rules

The aggregated entry point only passes arguments that an internal script supports to the corresponding provider, to avoid script errors caused by extra arguments.

- `category`
  - `arxiv_search.py`: passed as `category`
  - `deepxiv_search.py`: passed as `categories=[category]`
  - `arxiv_mirror_search.py`: passed as `category`
  - other providers: not passed
- `lang`
  - `google_scholar_search.py`: passed as `lang`
  - `wikipedia_search.py`: passed as `lang`
  - other providers: not passed

## Concurrency and timeouts

- Different sources run concurrently; for example `arxiv`, `semantic`, `wikipedia` start at the same time.
- Within the same source, providers run in fallback-chain order.
- Each provider times out after `60s` by default.
- A provider timeout is recorded as a failure for that provider, and the next provider in the same source is tried.

Example:

```bash
python3 scripts/search.py "transformer" \
  --source all \
  --provider-timeout 30
```

## Output format

The CLI stdout and the `--output` file use the same output format.

The top-level output does not contain an `items` field. Each source's results stay in `source_results[*].items`.

```json
{
  "success": true,
  "query": "NSA",
  "provider": "search.py",
  "sources": ["arxiv", "semantic"],
  "source_results": [
    {
      "source": "arxiv",
      "success": true,
      "provider": "arxiv_official",
      "items": [
        {
          "source": "arxiv",
          "provider": "arxiv_official",
          "provider_rating": null,
          "title": "Example title",
          "abstract": "Example abstract",
          "citation_count": null,
          "url": "https://arxiv.org/abs/..."
        }
      ],
      "attempts": [
        {
          "provider": "arxiv_official",
          "success": true,
          "count": 1,
          "error": null
        }
      ],
      "error": null
    }
  ],
  "errors": [],
  "error": null
}
```

If `--output` is used, the output additionally contains:

```json
{
  "output_path": "/absolute/path/to/results/search.json"
}
```

## Item fields

Every item tries to always include:

- `source`
- `provider`
- `provider_rating`, currently always `null`
- `title`
- `abstract`
- `citation_count`

Useful fields returned by the original provider are also preserved, for example:

- ArXiv: `arxiv_id`, `pdf_url`, `categories`, `doi`
- Semantic Scholar: `paper_id`, `doi`, `arxiv_id`, `venue`, `year`
- Google Scholar: `scholar_id`, `cited_by_url`, `pdf_url`
- PubMed: `pmid`, `pmc_id`, `journal`, `pub_date`, `doi`
- SSRN: `doi`, `year`, `publication_date`, `publisher`, `container`
- Wikipedia: `page_id`, `word_count`, `timestamp`, `section_title`

## Deduplication rules

Within the same source, items are deduplicated by stable ID. Different sources are never deduplicated against each other.

Deduplication fields, in priority order:

- `arxiv`: `arxiv_id`, `doi`, `paper_id`, `openalex_id`, `url`, `title`
- `semantic`: `paper_id`, `doi`, `arxiv_id`, `url`, `title`
- `google_scholar`: `scholar_id`, `doi`, `url`, `title`
- `pubmed`: `pmid`, `doi`, `pmc_id`, `url`, `title`
- `ssrn`: `doi`, `url`, `title`
- `wikipedia`: `page_id`, `url`, `title`

## Python API

You can also import and call it directly:

```python
from search import search

result = search(
    "NSA",
    sources=["arxiv", "semantic"],
    limit=5,
    category="cs.CL",
    provider_timeout=60,
)
```

Note: the internal result returned by the Python API keeps the top-level `items` for programmatic use; the CLI stdout and `--output` file strip the top-level `items` to avoid duplicate output.
