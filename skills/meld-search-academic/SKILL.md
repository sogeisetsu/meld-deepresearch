---
name: meld-search-academic
description: Academic literature search, paper full-text and section reading, and citation-tree tracing. Use when the user wants to search papers or encyclopedia entries across arXiv, Semantic Scholar, Google Scholar, PubMed, SSRN and Wikipedia, read arXiv or PMC full text, list paper sections, trace a paper's references and citations, or follow citation chains for related-work surveys and literature reviews.
license: MIT
metadata:
  author: sogeisetsu
  repository: https://github.com/sogeisetsu/meld-deepresearch
  version: "0.3.0"
---

# meld-search-academic - Academic search

## Credential configuration

API keys, tokens, and cookies are best stored in a `.env` file at the repository root (see `.env.example`) and loaded by the runtime or the user as environment variables of the same names before execution. Scripts still read credentials only from environment variables or explicit CLI arguments; never write real keys into the skill payload, reports, logs, or commits.

Use three unified entry points to complete academic research:

- `search.py`: search papers and encyclopedia entries
- `paper.py`: list paper sections, read a paper's full text or a specific section
- `refTree.py`: query a paper's references and citations

Do not call the historical provider scripts directly; they are only internal implementation details of the unified entry points.
When you need the provider fallback chain, parameter dispatch rules, or the full output fields, read `references/search.md`, `references/paper.md`, and `references/refTree.md` as needed.

## Available scripts

| Script | Purpose | Main input | Main output |
|------|------|----------|----------|
| `scripts/search.py` | Search papers/encyclopedia entries | `query`, optional `--source`, `--limit`, `--category`, `--lang` | Papers/encyclopedia entries grouped by source, in `source_results[*].items` |
| `scripts/paper.py` | List sections, read paper full text or a section | Paper ID, optional `--source`, `--list_section`, `--section` | Section list in `sections`; full text or section body in `content` |
| `scripts/refTree.py` | Query the citation tree | `--paper_id`, `--title`, optional `--direction` | References and citing papers, in `source_results[*].references` / `source_results[*].citations` |

## Execution conventions

All `scripts/...`, `requirements.txt`, and `references/...` paths in this skill are relative to this skill directory; if the current working directory is different, resolve them to absolute paths first, and do not rely on a `${SKILL_DIR}` runtime variable.

Calling conventions:

- Do not start multiple scripts of this skill in parallel; `search.py` and `refTree.py` already handle concurrency, timeouts, and provider fallback chains internally.
- For long results, prefer adding `--output <path>` to write to a file, then read the fields you need, to avoid overly long terminal output.
- `--provider-timeout` is the timeout for a single provider; by default the script's built-in timeout is used.

## Dependencies

On first run, or when a script reports a missing package, install this skill's core dependency list into the current Python environment:

```bash
python3 -m pip install -r requirements.txt
```

`requirements.txt` is the CORE list: it contains only the packages required by the official/public API paths, so it is always installable. The browser-crawler providers are an OPTIONAL degradation tier, declared separately in `requirements-optional.txt`:

```bash
python3 -m pip install -r requirements-optional.txt
```

playwright and camoufox are OPTIONAL. When they are missing, the skill degrades to (a) the official/public APIs already used by `arxiv_search.py`, `crossref_search.py`, `openalex_search.py`, `pubmed_search.py`, `semantic_scholar_search.py`, `ssrn_search.py`, `wikipedia_search.py`, and (b) the host's general web-search capability. Missing optional dependencies must never abort the skill: pick another provider or the generic fallback instead.

Do not install dependencies from inside the scripts. If installation fails, the network is unavailable, or a package cannot be installed, stop using the affected script and fall back to the host's general web-search capability or a browser automation tool, and state that the dependency is missing. Never name a specific host tool.

The crawler fallback additionally needs a runtime environment:

```bash
python3 -m playwright install firefox
```

`arxiv_crawler_search.py` and `semantic_scholar_crawler_refTree.py` also need Node.js, plus a `node_modules/camoufox-js` installed in the current directory or one of its ancestors. When these are missing, do not try to bypass them; use a non-crawler provider or web search instead.

## Hand-off entry & exit

- **Entry:** this skill works standalone, and may also be handed off to from
  `skills/meld-deepresearch` as documented in that skill's
  `references/protocol.md` §2a — academic or historical subjects come to
  `meld-search-academic`.
- **Exit:** when invoked as a hand-off, return reproducible numbers/quotes
  plus the exact re-runnable command, so the caller can record them as
  `observations[]`/`sources[]`; never write into the caller's evidence files.
  If a dependency or the sibling skill is missing, degrade and say so instead
  of failing.

## Arguments

### search.py

Unified search entry point. By default it searches all supported sources and returns results grouped by source.

```bash
python3 scripts/search.py <query> [options]
```

| Argument | Description | Default |
|------|------|--------|
| `query` | Search keywords, required positional argument | - |
| `--source`, `--sources`, `-s` | Search sources; repeatable or comma-separated | `all` |
| `--limit`, `-n` | Number of results per source | `10` |
| `--category`, `-c` | ArXiv category filter, only passed to sources that support categories | - |
| `--lang`, `-l` | Language hint, only passed to sources that support a language argument | - |
| `--output`, `-o` | Write the final JSON to a file | - |
| `--provider-timeout` | Timeout per provider in seconds; `0` means no limit | `60` |

Supported `--source` values:

- `all`
- `arxiv`
- `semantic`
- `google_scholar`
- `pubmed`
- `ssrn`
- `wikipedia`

Examples:

```bash
python3 scripts/search.py "retrieval augmented generation" --limit 5
python3 scripts/search.py "diffusion model" --source arxiv,semantic --category cs.CV --limit 5
python3 scripts/search.py "Alzheimer's disease multimodal diagnosis" --source pubmed,wikipedia --lang zh --limit 5
python3 scripts/search.py "open source governance" --source ssrn --limit 10
python3 scripts/search.py "agentic memory" --source all --limit 8 --output results/search.json
```

### paper.py

Unified paper-reading entry point. By default it reads arXiv papers; pass `--source pmc` explicitly to read PMC papers. If you are unsure of a section name, first list the available sections with `--list_section`, then read a section in depth with `--section`.

```bash
python3 scripts/paper.py <id> [options]
```

| Argument | Description | Default |
|------|------|--------|
| `id` | Paper ID. arXiv accepts the raw ID, the `arXiv:` prefix, abs/pdf URLs; PMC accepts `PMC11119143`, `11119143`, PMC URLs | - |
| `--source` | Paper source: `arxiv` or `pmc` | `arxiv` |
| `--section`, `-s` | Read a specific section; omit to read the full text | - |
| `--list_section`, `--list-section` | List the paper's available sections without returning the body; cannot be combined with `--section` | false |
| `--output`, `-o` | Write the final JSON to a file | - |

Examples:

```bash
python3 scripts/paper.py 2603.00729
python3 scripts/paper.py 2603.00729 --list_section
python3 scripts/paper.py arXiv:2603.00729 --section introduction
python3 scripts/paper.py 2603.00729 --section method --output results/paper-method.json
python3 scripts/paper.py PMC11119143 --source pmc
python3 scripts/paper.py PMC11119143 --source pmc --list-section
python3 scripts/paper.py PMC11119143 --source pmc --section results
```

### refTree.py

Unified citation-tree entry point. Both `--paper_id` and `--title` are required; the title is used for exact matching during fallback.

```bash
python3 scripts/refTree.py --paper_id <paper_id> --title <title> [options]
```

| Argument | Description | Default |
|------|------|--------|
| `--paper_id` | Paper ID: Semantic Scholar ID, DOI, ArXiv ID, PMID, etc. | - |
| `--title` | Paper title, required | - |
| `--direction` | Query direction: `references` or `citations`; omit to query both | - |
| `--source`, `--sources`, `-s` | Citation-tree source; currently `all`, `semantic` | `all` |
| `--limit`, `-n` | Number of results per source, per direction | `10` |
| `--api-key` | Semantic Scholar API key, optional | - |
| `--provider-timeout` | Timeout per provider in seconds; `0` means no limit | `60` |
| `--output`, `-o` | Write the final JSON to a file | - |

Note: the argument name is `--paper_id`, not `--paper-id`; `paper_id` does not accept a positional argument.

Examples:

```bash
python3 scripts/refTree.py --paper_id "2309.16609" --title "Qwen Technical Report"
python3 scripts/refTree.py --paper_id "2309.16609" --title "Qwen Technical Report" --direction references --limit 20
python3 scripts/refTree.py --paper_id "10.1038/s41586-024-07487-w" --title "AlphaFold 3" --direction citations
python3 scripts/refTree.py --paper_id "2309.16609" --title "Qwen Technical Report" --output results/refTree.json
```

## Output format

All scripts output JSON. Check the top-level `success` first; on failure read `error`, `errors`, and `attempts` to determine whether there were no results, a timeout, or a provider failure.

### search.py output

The top level of the CLI output does not contain `items`; paper entries are in `source_results[*].items`:

```json
{
  "success": true,
  "query": "retrieval augmented generation",
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
          "title": "Example title",
          "abstract": "Example abstract",
          "citation_count": null,
          "arxiv_id": "2301.00001",
          "url": "https://arxiv.org/abs/2301.00001"
        }
      ],
      "attempts": [],
      "error": null
    }
  ],
  "errors": [],
  "error": null
}
```

Common item fields:

- Generic: `title`, `abstract`, `snippet`, `url`, `citation_count`, `doi`
- arXiv: `arxiv_id`, `pdf_url`, `categories`
- Semantic Scholar: `paper_id`, `venue`, `year`
- SSRN: `doi`, `year`, `publication_date`, `publisher`, `container` (`container` is the SSRN working paper series name, e.g. "SSRN Electronic Journal")
- PubMed: `pmid`, `pmc_id`, `journal`, `pub_date`
- Wikipedia: `page_id`, `word_count`, `section_title`

### paper.py output

By default it reads the full text; with `--section` it reads a section. The body is in the top-level `content`:

```json
{
  "success": true,
  "source": "arxiv",
  "provider": "arxiv_html",
  "arxiv_id": "2603.00729",
  "section": "introduction",
  "content": "<full text or section body>",
  "char_count": 12345,
  "attempts": [],
  "error": null
}
```

With `--list_section` it returns only the section structure, without `content`:

```json
{
  "success": true,
  "source": "arxiv",
  "provider": "arxiv_html",
  "arxiv_id": "2603.00729",
  "section_count": 2,
  "sections": [
    {"name": "Abstract", "level": 0},
    {"name": "1 Introduction", "level": 1}
  ],
  "attempts": [],
  "error": null
}
```

Common fields:

- arXiv: `arxiv_id`, `title`, `abs_url`, `html_url`, `pdf_url`, `section_count`, `sections`
- PMC: `pmc_id`, `pmid`, `title`, `pmc_url`, `section_count`, `sections`
- With `--list_section` it returns `sections` and `section_count`, without `content`
- With `--section` the output includes `section`; without `--list_section` / `--section` it reads the full text

### refTree.py output

Citation-tree results are in `source_results[*].references` and `source_results[*].citations`:

```json
{
  "success": true,
  "id": "2309.16609",
  "title": "Qwen Technical Report",
  "provider": "refTree.py",
  "direction": "all",
  "source_results": [
    {
      "source": "semantic",
      "success": true,
      "provider": "semantic_official",
      "references": [
        {
          "title": "Example reference",
          "abstract": "Example abstract",
          "citation_count": 128,
          "paper_id": "example-reference-id",
          "arxiv_id": "2301.00001"
        }
      ],
      "citations": [
        {
          "title": "Example citing paper",
          "abstract": "Example abstract",
          "citation_count": 42,
          "paper_id": "example-citing-id",
          "doi": "10.1234/example"
        }
      ],
      "attempts": [],
      "error": null
    }
  ],
  "errors": [],
  "error": null
}
```

If `--output` is used, all three scripts additionally include `output_path` in the JSON.

## Concurrency and rate-limiting conventions

These scripts access external academic services, so request frequency must be controlled.
When running this skill's scripts:
- Do not run multiple search scripts concurrently.
- Do not use parallel tools to invoke multiple `python3 scripts/...` commands at once.
- Run one script command at a time and wait for the result before running the next one.
- For batch queries, prefer the script's own parameters such as `--limit` and `--id-list` instead of starting multiple processes.
- If you need consecutive calls, execute them in order and wait a few seconds when necessary.

## Full-text reading workflow

When search results only contain abstracts, use `paper.py` first to list sections, then fetch the full text or key sections.

1. Search with `search.py` first, and record `title`, `arxiv_id`, `pmc_id`, `paper_id`, `doi`, `citation_count` from `source_results[*].items`.
2. If an entry has `arxiv_id`, first run `python3 scripts/paper.py <arxiv_id> --source arxiv --list_section` to see the sections; then read in depth with `--section <section>`.
3. If an entry has `pmc_id`, first run `python3 scripts/paper.py <pmc_id> --source pmc --list_section` to see the sections; then read `--section <section>` as needed.
4. For an overall understanding, read the full text without `--section` / `--list_section`.
5. When the full text is long, use `--output results/paper.json`, then read the `content`, `sections`, `char_count` fields.

## Citation tracing workflow

Discover related work that keyword search does not cover by following papers' citation relationships.

Use references to find foundational work, and citations to find follow-up progress. `refTree.py` needs both the paper ID and the title.

**Backward tracing (find foundational work)**:


1. Keyword search finds a highly relevant paper -> take its `paper_id` or `arxiv_id` and `title`
2. `refTree.py --paper_id "<id>" --title "<title>" --direction references --limit 20`  -> find highly cited references
3. Filter entries relevant to the research question -> read them in depth with `paper.py`

**Forward tracing (find follow-up progress)**:

1. Find a foundational or key paper in the field -> take its ID
2. `refTree.py --paper_id "<id>" --title "<title>" --direction citations --limit 20` -> find recent highly cited follow-up work
3. Filter entries relevant to the research question -> read them in depth with `paper.py`

**Citation chains: build an evolution path**

1. Start from seed paper A -> backward to find A's key reference B
2. From B -> forward to find later work citing B (you may discover relevant paper C that A did not cite)
3. Form the knowledge threads B -> A -> ... and B -> C -> ...

## Main workflow
Strictly follow this workflow to execute the full academic search process

1. Search academic literature on all possibly relevant platforms among the provided academic platforms
2. When the abstract is insufficient or the paper is highly relevant, list the sections, try reading paper sections or the full text, and judge the paper's relevance to the search need
3. Select highly relevant papers and search their references and citations (use the citation tracing workflow).
4. Select the highly cited papers in the citation tree, and repeat steps 2 and 3.
5. Repeat the above steps for multiple rounds of searching, searching as much as possible.
6. Stop searching when the volume of literature, citation chains, and full-text evidence is enough to support the answer, and state the main basis in the conclusion.

## ArXiv category quick reference

Top-level fields can be used directly (e.g. `--category cs`); subcategories are more precise (e.g. `--category cs.AI`).

| Field | Category code | Description |
|------|---------|------|
| **Computer science** | `cs.AI` | Artificial intelligence |
| | `cs.LG` | Machine learning |
| | `cs.CL` | Computational linguistics / NLP |
| | `cs.CV` | Computer vision |
| | `cs.IR` | Information retrieval |
| | `cs.RO` | Robotics |
| | `cs.SE` | Software engineering |
| | `cs.DC` | Distributed / parallel computing |
| | `cs.NI` | Networking and Internet |
| | `cs.CR` | Cryptography and security |
| | `cs.DB` | Databases |
| | `cs.HC` | Human-computer interaction |
| **Statistics** | `stat.ML` | Statistical machine learning |
| | `stat.AP` | Applied statistics |
| | `stat.ME` | Statistical methodology |
| **Mathematics** | `math.OC` | Optimization and control |
| | `math.ST` | Statistics theory |
| | `math.CO` | Combinatorics |
| **Physics** | `physics` | Physics (whole class) |
| | `cond-mat` | Condensed matter physics |
| | `quant-ph` | Quantum physics |
| | `hep-th` | High-energy theory |
| **Economics / finance** | `econ.GN` | General economics |
| | `q-fin.CP` | Computational finance |
| | `q-fin.ST` | Statistical finance |
| **Biology / medicine** | `q-bio.NC` | Neuroscience |
| | `q-bio.GN` | Genomics |
| | `q-bio.QM` | Quantitative methods |

## Platform notes (pure Windows)

- Run scripts with `python` when `python3` is not on `PATH` (on stock Windows
  `python3` may be the Microsoft Store stub). Every command in this skill is
  written as `python3 …`; substituting `python` is the only change needed.
- The scripts use `pathlib.Path` throughout and never assume a POSIX temp
  directory, a POSIX shell or `/` separators, so no other change is required.
- The optional crawler tier additionally needs Node.js on `PATH`; when it is
  missing the skill degrades exactly as it does for a missing Python package.
