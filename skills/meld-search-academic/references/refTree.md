# refTree.py unified citation-tree entry point

`refTree.py` aggregates the refTree scripts in the `meld-search-academic/scripts` directory, queries a paper's references and citing papers, and outputs one unified JSON.

It only aggregates citation-tree functionality; it does not include `search` or `paper`.

## Basic usage

Query a paper's references and citing papers:

```bash
python3 scripts/refTree.py \
  --paper_id "2309.16609" \
  --title "Qwen Technical Report"
```

Query only references:

```bash
python3 scripts/refTree.py \
  --paper_id "2309.16609" \
  --title "Qwen Technical Report" \
  --direction references
```

Query only citing papers:

```bash
python3 scripts/refTree.py \
  --paper_id "2309.16609" \
  --title "Qwen Technical Report" \
  --direction citations
```

Write to a JSON file:

```bash
python3 scripts/refTree.py \
  --paper_id "2309.16609" \
  --title "Qwen Technical Report" \
  --limit 20 \
  --output results/refTree.json
```

## Arguments

| Argument | Description | Default |
| --- | --- | --- |
| `--paper_id` | Paper ID, required. Accepts Semantic Scholar paper ID, DOI, ArXiv ID, PMID, and other formats the underlying scripts can recognize | none |
| `--title` | Paper title, required. The crawler fallback uses it for exact matching after the official provider fails | none |
| `--direction` | Query direction; supports `references` or `citations`. Omit to query both directions | none |
| `--source`, `--sources`, `-s` | Search sources; currently `all`, `semantic` | `all` |
| `--limit`, `-n` | Number of results per source, per direction | `10` |
| `--output`, `-o` | Write the final JSON result to the given file; parent directories are created automatically | none |
| `--api-key` | Semantic Scholar API key, only passed to the official Semantic Scholar provider | none |
| `--provider-timeout` | Timeout per provider call in seconds; `0` means no limit | `60` |

Note: `paper_id` is always passed as `--paper_id "<paper_id>"`; positional arguments are not supported, and neither is `--paper-id`.

## Supported sources

Currently only:

- `semantic`

`--source all` is equivalent to:

```text
semantic
```

## Provider fallback chain

### semantic

1. `semantic_scholar_refTree.py` -> `semantic_official`
2. `semantic_scholar_crawler_refTree.py` -> `semantic_crawler`

`semantic_official` prefers the Semantic Scholar SDK; when the SDK is unavailable or a request fails, the underlying script falls back to a Semantic Scholar Graph API HTTP request.

`semantic_crawler` is a page-crawling fallback and requires the runtime environment of `semantic_scholar_crawler_refTree.py` to be available, including Playwright, Node.js, and `camoufox-js`. When those optional dependencies are missing, the crawler reports a degraded failure instead of aborting, and the chain continues with the official provider or the generic web search.

## Direction fallback logic

### Direction specified

If you pass:

```bash
--direction references
```

or:

```bash
--direction citations
```

only that direction is queried:

1. First call `semantic_official`
2. If it fails, then call `semantic_crawler`

### Direction not specified

Without `--direction`, both directions are queried by default:

- `references`
- `citations`

Execution logic:

1. Call `semantic_official` concurrently for `references` and `citations`
2. If only one direction fails, use `semantic_crawler` only to re-query the failed direction
3. If both directions fail, call `semantic_crawler` exactly once without a direction, letting the crawler query both directions by default

## Parameter dispatch rules

The unified entry point only passes arguments that an internal script supports to the corresponding provider, to avoid script errors caused by extra arguments.

### semantic_official

Passed:

- `paper_id`
- `direction`
- `limit`
- `api_key`

Internally fixed filter parameters:

- `min_citations=0`
- `year_min=None`
- `year_max=None`

Not passed:

- `title`
- `output`
- `source`
- `provider_timeout`

### semantic_crawler

Passed:

- `title`
- `direction`, only when the direction needs to be restricted; not passed when both directions failed
- `limit`

Internally fixed run parameters:

- `headless=True`
- `max_pages=None`
- a temporary `output` file path

Not passed:

- `paper_id`
- `api_key`
- `source`
- `provider_timeout`

## Output format

The CLI stdout and the `--output` file use the same output format.

Success example:

```json
{
  "success": true,
  "id": "2309.16609",
  "title": "Qwen Technical Report",
  "provider": "refTree.py",
  "sources": ["semantic"],
  "direction": "all",
  "source_results": [
    {
      "source": "semantic",
      "success": true,
      "provider": "semantic_official",
      "provider_rating": null,
      "citations": [
        {
          "source": "semantic",
          "id": "example-citing-paper-id",
          "title": "Example citing paper",
          "provider": "semantic_official",
          "provider_rating": null,
          "citation_count": 42,
          "abstract": "Example abstract",
          "paper_id": "example-citing-paper-id",
          "doi": "10.1234/example"
        }
      ],
      "references": [
        {
          "source": "semantic",
          "id": "example-reference-paper-id",
          "title": "Example referenced paper",
          "provider": "semantic_official",
          "provider_rating": null,
          "citation_count": 128,
          "abstract": "Example abstract",
          "paper_id": "example-reference-paper-id",
          "arxiv_id": "2301.00001"
        }
      ],
      "attempts": [
        {
          "provider": "semantic_official",
          "direction": "references",
          "success": true,
          "count": 10,
          "error": null
        },
        {
          "provider": "semantic_official",
          "direction": "citations",
          "success": true,
          "count": 10,
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

`source_results` holds each source's results and internal execution details. Each element contains that source's `citations`, `references`, the provider actually used, whether each provider attempt succeeded, the returned count, and error messages. The paper lists are not placed in top-level fields; when consuming paper results, read `source_results[*].citations` and `source_results[*].references`.

If `--output` is used, the output additionally contains:

```json
{
  "output_path": "/absolute/path/to/results/refTree.json"
}
```

Failure example:

```json
{
  "success": false,
  "id": "2309.16609",
  "title": "Qwen Technical Report",
  "provider": "refTree.py",
  "sources": ["semantic"],
  "direction": "references",
  "source_results": [
    {
      "source": "semantic",
      "success": false,
      "provider": null,
      "provider_rating": null,
      "citations": [],
      "references": [],
      "attempts": [
        {
          "provider": "semantic_official",
          "direction": "references",
          "success": false,
          "count": 0,
          "error": "provider error"
        },
        {
          "provider": "semantic_crawler",
          "direction": "references",
          "success": false,
          "count": 0,
          "error": "provider error"
        }
      ],
      "error": "semantic_official[references]: provider error; semantic_crawler[references]: provider error"
    }
  ],
  "errors": [
    {
      "source": "semantic",
      "error": "semantic_official[references]: provider error; semantic_crawler[references]: provider error",
      "attempts": [
        {
          "provider": "semantic_official",
          "direction": "references",
          "success": false,
          "count": 0,
          "error": "provider error"
        },
        {
          "provider": "semantic_crawler",
          "direction": "references",
          "success": false,
          "count": 0,
          "error": "provider error"
        }
      ]
    }
  ],
  "error": "All selected sources failed"
}
```

## Article fields

Every article in `source_results[*].citations` and `source_results[*].references` tries to always include:

- `source`
- `id`
- `title`
- `provider`
- `provider_rating`, currently always `null`
- `citation_count`

Useful fields returned by the underlying provider are also preserved, for example:

- `abstract`
- `url`
- `snippet`
- `authors`
- `year`
- `venue`
- `publication_date`
- `doi`
- `arxiv_id`
- `paper_id`
- `influential_citation_count`
- `is_open_access`
- `open_access_pdf`
- `fields_of_study`
- `citation_contexts`
- `citation_intents`

## Deduplication rules

Within the same source, items are deduplicated by stable ID. Different sources are never deduplicated against each other.

Deduplication fields for the `semantic` source, in priority order:

1. `paper_id`
2. `doi`
3. `arxiv_id`
4. `url`
5. `title`

If the crawler only returns a Semantic Scholar URL, `refTree.py` tries to extract the paper ID from the URL and fills it into the unified fields `id` and `paper_id`.

## Python API

You can also import and call it directly:

```python
from refTree import ref_tree

result = ref_tree(
    paper_id="2309.16609",
    title="Qwen Technical Report",
    sources=["semantic"],
    direction=None,
    limit=10,
    provider_timeout=60,
    api_key=None,
)
```

The return value has the same structure as the CLI stdout JSON.

## When to use

- First search papers with `search.py` to get a `paper_id`, `arxiv_id`, or DOI
- Use `refTree.py` to query the paper's `references` and find foundational work
- Use `refTree.py` to query the paper's `citations` and find follow-up progress
- Continue reading the full text or sections of the returned highly cited papers with `paper.py`
