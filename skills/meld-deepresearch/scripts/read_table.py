#!/usr/bin/env python
"""Read a local spreadsheet or Word document with the standard library only.

Intended to be run by the skill when a research task supplies local data files
(`.xlsx`, `.csv`, `.tsv`, `.docx`). The run should record the exact command as
an `observations[]` entry and cite every figure computed from it with `[^oN]`.

Zero third-party dependencies. Handles:
* `.xlsx`  — sheet mapping via workbook rels (not a hard-coded `sheet1.xml`),
  shared strings, inline/formula/boolean/error cells, sparse cells, and Excel
  serial dates via `styles.xml` + `date1904`;
* `.csv` / `.tsv` — dialect sniffing;
* `.docx` — paragraphs, heading styles and tables, as structured blocks
  (`--format json`) or as Markdown (`--format md`).

Examples:
  python read_table.py data.xlsx --sheet Sheet1
  python read_table.py data.xlsx --all-sheets --format json
  python read_table.py data.csv --max-rows 50
  python read_table.py data.xlsx --format md
  python read_table.py report.docx --format md
  python read_table.py report.docx --format json
  python read_table.py --selftest
"""
import argparse
import csv
import datetime
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BUILTIN_DATE_FMT = set(list(range(14, 23)) + list(range(45, 48)) +
                       [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 50, 51, 52, 53, 54, 55, 56, 57, 58])
COL_RE = re.compile(r"([A-Za-z]+)")
ROW_RE = re.compile(r"(\d+)")


# ---- namespace-agnostic XML helpers (support transitional + strict OOXML) ----
def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _kids(el, name):
    return [c for c in list(el) if _local(c.tag) == name]


def _first(el, name):
    for c in list(el):
        if _local(c.tag) == name:
            return c
    return None


def _text(el):
    return "".join(t.text or "" for t in el.iter() if _local(t.tag) == "t")


# ---- xlsx ----
def col_index(ref):
    m = COL_RE.match(ref or "")
    if not m:
        return 0
    n = 0
    for ch in m.group(1).upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _is_date_code(code):
    c = re.sub(r"\[[^\]]*\]", "", code or "")
    c = re.sub(r'"[^"]*"', "", c)
    return bool(re.search(r"[yYdDhHsS]", c))


def read_styles(z):
    date_styles, custom = set(), {}
    try:
        root = ET.fromstring(z.read("xl/styles.xml"))
    except KeyError:
        return date_styles
    numfmts = _first(root, "numFmts")
    if numfmts is not None:
        for nf in _kids(numfmts, "numFmt"):
            custom[int(nf.get("numFmtId"))] = nf.get("formatCode")
    cellxfs = _first(root, "cellXfs")
    if cellxfs is not None:
        for i, xf in enumerate(_kids(cellxfs, "xf")):
            nid = int(xf.get("numFmtId") or 0)
            code = custom.get(nid)
            if nid in BUILTIN_DATE_FMT or (code and _is_date_code(code)):
                date_styles.add(i)
    return date_styles


def read_shared(z):
    out = []
    try:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return out
    for si in _kids(root, "si"):
        out.append(_text(si))
    return out


def read_sheet_meta(z):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    date1904 = False
    pr = _first(wb, "workbookPr")
    if pr is not None and str(pr.get("date1904")).lower() in ("1", "true"):
        date1904 = True
    rels = {}
    try:
        rroot = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        for rel in _kids(rroot, "Relationship"):
            rels[rel.get("Id")] = rel.get("Target")
    except KeyError:
        pass
    sheets = []
    sh = _first(wb, "sheets")
    for i, s in enumerate(_kids(sh, "sheet") if sh is not None else []):
        rid = None
        for k, v in s.attrib.items():
            if _local(k) == "id":
                rid = v
        target = rels.get(rid, "")
        if target.startswith("/"):
            target = target[1:]
        elif not target.startswith("xl/"):
            target = "xl/" + target
        sheets.append({"name": s.get("name"), "state": s.get("state") or "visible",
                       "index": i, "target": target})
    return sheets, date1904


def excel_serial(num, date1904):
    base = datetime.datetime(1904, 1, 1) if date1904 else datetime.datetime(1899, 12, 30)
    dt = base + datetime.timedelta(days=num)
    if abs(num - int(num)) < 1e-9:
        return dt.date().isoformat()
    return dt.replace(microsecond=0).isoformat(sep=" ")


def parse_sheet(z, target, shared, date_styles, date1904, max_rows):
    root = ET.fromstring(z.read(target))
    data = _first(root, "sheetData")
    if data is None:
        return []
    cells_by_row, maxr = {}, 0
    for row in _kids(data, "row"):
        rn = int(row.get("r") or (maxr + 1))
        maxr = max(maxr, rn)
        cells = {}
        for c in _kids(row, "c"):
            ci = col_index(c.get("r"))
            t = c.get("t") or "n"
            s = c.get("s")
            si = int(s) if s is not None else None
            v = _first(c, "v")
            if t == "inlineStr":
                isv = _first(c, "is")
                val = _text(isv) if isv is not None else None
            elif t == "s" and v is not None and v.text is not None:
                val = shared[int(v.text)]
            elif t == "str":
                val = v.text if v is not None else None
            elif t == "b":
                val = bool(v is not None and v.text == "1")
            elif t == "e":
                val = v.text if v is not None else None
            else:
                if v is None or v.text is None:
                    val = None
                else:
                    num = float(v.text)
                    if si is not None and si in date_styles:
                        val = excel_serial(num, date1904)
                    else:
                        val = int(num) if float(num).is_integer() else num
            cells[ci] = val
        cells_by_row[rn] = cells
    rows = []
    for rn in range(1, maxr + 1):
        cells = cells_by_row.get(rn, {})
        if cells:
            w = max(cells) + 1
            rows.append([cells.get(i) for i in range(w)])
        else:
            rows.append([])
        if max_rows and len(rows) >= max_rows:
            break
    width = max((len(r) for r in rows), default=0)
    for r in rows:
        r.extend([None] * (width - len(r)))
    return rows


def read_xlsx(source):
    z = zipfile.ZipFile(source)
    shared = read_shared(z)
    date_styles = read_styles(z)
    sheets, date1904 = read_sheet_meta(z)
    return z, sheets, shared, date_styles, date1904


def read_delimited(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        rows = [[(c if c != "" else None) for c in r] for r in csv.reader(fh, dialect)]
    return rows


# ---- docx (salvaged from test/tools/docx_to_md.py, generalised) ----
def read_docx(path):
    """Return the document body as ordered blocks.

    Each block is ``{"type": "heading"|"paragraph"|"table", ...}``; a heading
    carries ``text``, a paragraph carries ``text``, a table carries ``rows``.
    Empty paragraphs are dropped.
    """
    with zipfile.ZipFile(path) as z:
        try:
            root = ET.fromstring(z.read("word/document.xml"))
        except KeyError:
            raise SystemExit("not a .docx: %s has no word/document.xml" % path)
    body = None
    for child in list(root):
        if _local(child.tag) == "body":
            body = child
            break
    if body is None:
        raise SystemExit("malformed .docx: %s has no document body" % path)
    blocks = []
    for el in list(body):
        name = _local(el.tag)
        if name == "p":
            text = "".join(
                t.text or "" for t in el.iter() if _local(t.tag) == "t").strip()
            if not text:
                continue
            style = ""
            ppr = _first(el, "pPr")
            if ppr is not None:
                pstyle = _first(ppr, "pStyle")
                if pstyle is not None:
                    style = (pstyle.get(WORD_NS + "val")
                             or pstyle.get("val") or "")
            lowered = style.lower()
            if lowered.startswith("heading") or (style[:1].isdigit()):
                blocks.append({"type": "heading", "text": text})
            else:
                blocks.append({"type": "paragraph", "text": text})
        elif name == "tbl":
            rows = []
            for tr in _kids(el, "tr"):
                cells = []
                for tc in _kids(tr, "tc"):
                    cells.append(" ".join(
                        "".join(t.text or "" for t in p.iter()
                                if _local(t.tag) == "t").strip()
                        for p in _kids(tc, "p")).strip())
                rows.append(cells)
            if rows:
                blocks.append({"type": "table", "rows": rows})
    return blocks


def blocks_to_markdown(blocks):
    """Render docx blocks as Markdown (headings, paragraphs, GFM tables)."""
    lines = []
    for block in blocks:
        if block["type"] == "heading":
            lines.append("## " + block["text"])
        elif block["type"] == "paragraph":
            lines.append(block["text"])
        else:
            rows = block["rows"]
            width = max(len(r) for r in rows)
            for index, row in enumerate(rows):
                padded = list(row) + [""] * (width - len(row))
                lines.append("| " + " | ".join(padded) + " |")
                if index == 0:
                    lines.append("|" + "---|" * width)
            lines.append("")
    out = []
    for line in lines:
        if line == "" and out and out[-1] == "":
            continue
        out.append(line)
    return "\n".join(out).rstrip("\n") + "\n"


def rows_to_markdown(header, rows):
    """Render a sheet as a Markdown table (the --format md path)."""
    data = ([header] if header else []) + list(rows)
    if not data:
        return ""
    width = max(len(r) for r in data)
    lines = []
    for index, row in enumerate(data):
        padded = ["" if v is None else str(v) for v in row]
        padded = padded + [""] * (width - len(padded))
        lines.append("| " + " | ".join(padded) + " |")
        if index == 0:
            lines.append("|" + "---|" * width)
    return "\n".join(lines) + "\n"


def to_result(path, all_sheets, sheet_sel, header, max_rows):
    name = path
    if path.lower().endswith(".docx"):
        return {"file": name, "kind": "docx", "blocks": read_docx(path)}
    if path.lower().endswith(".csv") or path.lower().endswith(".tsv"):
        rows = read_delimited(path)
        return {"file": name, "kind": "delimited", "sheet": "csv", "sheets": [],
                "header": rows[0] if (header and rows) else None,
                "rows": rows[1:] if (header and rows) else rows,
                "n_rows": (len(rows) - 1) if (header and rows) else len(rows)}
    z, sheets, shared, date_styles, date1904 = read_xlsx(path)
    result = {"file": name, "kind": "xlsx", "date1904": date1904,
              "sheets": [{"name": s["name"], "state": s["state"]} for s in sheets]}
    chosen = sheets
    if not all_sheets:
        if sheet_sel is None:
            vis = [s for s in sheets if s["state"] == "visible"] or sheets
            chosen = vis[:1]
        else:
            if sheet_sel.isdigit():
                chosen = [sheets[int(sheet_sel)]]
            else:
                chosen = [s for s in sheets if s["name"] == sheet_sel]
        if not chosen:
            raise SystemExit("sheet not found: %s (available: %s)"
                             % (sheet_sel, [s["name"] for s in sheets]))
    if all_sheets:
        out = []
        for s in chosen:
            rows = parse_sheet(z, s["target"], shared, date_styles, date1904, max_rows)
            out.append({"sheet": s["name"], "state": s["state"],
                        "header": rows[0] if (header and rows) else None,
                        "rows": rows[1:] if (header and rows) else rows,
                        "n_rows": (len(rows) - 1) if (header and rows) else len(rows)})
        result["all_sheets"] = out
        return result
    s = chosen[0]
    rows = parse_sheet(z, s["target"], shared, date_styles, date1904, max_rows)
    result["sheet"] = s["name"]
    result["header"] = rows[0] if (header and rows) else None
    result["rows"] = rows[1:] if (header and rows) else rows
    result["n_rows"] = (len(rows) - 1) if (header and rows) else len(rows)
    return result


# ---- self-test: build a minimal xlsx in memory and read it back ----
def _build_fixture():
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
    wb = ('<?xml version="1.0"?><workbook xmlns="%s" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<workbookPr date1904="0"/><sheets>'
          '<sheet name="Sheet1" sheetId="1" r:id="rId1"/>'
          '<sheet name="Sheet2" sheetId="2" r:id="rId2"/></sheets></workbook>') % MAIN_NS[1:-1]
    rels = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Target="worksheets/sheet2.xml"/>'
            '<Relationship Id="rId3" Target="sharedStrings.xml"/>'
            '<Relationship Id="rId4" Target="styles.xml"/></Relationships>')
    sst = ('<?xml version="1.0"?><sst xmlns="%s" count="2" uniqueCount="2">'
           '<si><t>姓名</t></si><si><t>人员甲</t></si></sst>') % MAIN_NS[1:-1]
    styles = ('<?xml version="1.0"?><styleSheet xmlns="%s">'
              '<cellXfs count="2"><xf numFmtId="0"/><xf numFmtId="14"/></cellXfs>'
              '</styleSheet>') % MAIN_NS[1:-1]
    # A1 shared string, B1 inline string; row2: A2 shared, B2 number, C2 date(s=1), D2 bool;
    # row4 is sparse (skips row 3).
    sheet1 = ('<?xml version="1.0"?><worksheet xmlns="%s"><sheetData>'
              '<row r="1"><c r="A1" t="s"><v>0</v></c>'
              '<c r="B1" t="inlineStr"><is><t>岗位</t></is></c></row>'
              '<row r="2"><c r="A2" t="s"><v>1</v></c>'
              '<c r="B2"><v>3.5</v></c>'
              '<c r="C2" s="1"><v>44927</v></c>'
              '<c r="D2" t="b"><v>1</v></c></row>'
              '<row r="4"><c r="A4" t="s"><v>0</v></c></row>'
              '</sheetData></worksheet>') % MAIN_NS[1:-1]
    sheet2 = ('<?xml version="1.0"?><worksheet xmlns="%s"><sheetData>'
              '<row r="1"><c r="A1" t="inlineStr"><is><t>x</t></is></c></row>'
              '</sheetData></worksheet>') % MAIN_NS[1:-1]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", rels)
        z.writestr("xl/sharedStrings.xml", sst)
        z.writestr("xl/styles.xml", styles)
        z.writestr("xl/worksheets/sheet1.xml", sheet1)
        z.writestr("xl/worksheets/sheet2.xml", sheet2)
    buf.seek(0)
    return buf


def _build_docx_fixture():
    """Minimal Word file: a heading, a paragraph and a 2x2 table."""
    doc = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
        "<w:r><w:t>季度概览</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>本季度营收增长12%。</w:t></w:r></w:p>"
        "<w:tbl>"
        '<w:tr><w:tc><w:p><w:r><w:t>岗位</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:t>均分</w:t></w:r></w:p></w:tc></w:tr>'
        '<w:tr><w:tc><w:p><w:r><w:t>岗位1</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:t>64.17</w:t></w:r></w:p></w:tc></w:tr>'
        "</w:tbl>"
        "</w:body></w:document>"
    ).encode("utf-8")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("word/document.xml", doc)
    return buf.getvalue()


def selftest():
    z, sheets, shared, date_styles, date1904 = read_xlsx(_build_fixture())
    assert [s["name"] for s in sheets] == ["Sheet1", "Sheet2"], sheets
    assert date_styles == {1}, date_styles
    assert shared == ["姓名", "人员甲"], shared
    rows = parse_sheet(z, sheets[0]["target"], shared, date_styles, date1904, 0)
    assert rows[0] == ["姓名", "岗位", None, None], rows[0]
    assert rows[1][0] == "人员甲" and rows[1][1] == 3.5, rows[1]
    assert rows[1][2] == "2023-01-01", rows[1][2]
    assert rows[1][3] is True, rows[1][3]
    assert rows[2] == [None, None, None, None] and rows[3][0] == "姓名", rows[2:4]

    # --docx path: build a Word file in memory and read it back.
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as fh:
        fh.write(_build_docx_fixture())
        docx_path = fh.name
    try:
        blocks = read_docx(docx_path)
        assert [b["type"] for b in blocks] == ["heading", "paragraph", "table"], blocks
        assert blocks[0]["text"] == "季度概览", blocks[0]
        assert blocks[1]["text"] == "本季度营收增长12%。", blocks[1]
        assert blocks[2]["rows"] == [["岗位", "均分"], ["岗位1", "64.17"]], blocks[2]
        md = blocks_to_markdown(blocks)
        assert "## 季度概览" in md and "| 岗位 | 均分 |" in md, md
        table_md = rows_to_markdown(["a", "b"], [[1, 2]])
        assert table_md.startswith("| a | b |"), table_md
    finally:
        import os
        os.unlink(docx_path)

    print("read_table selftest: OK (sheets, shared/inline strings, number, "
          "boolean, date, sparse, docx)")
    return 0


def emit_error(message):
    """Bad input: one JSON object on stdout (skill convention: exit 2)."""
    sys.stdout.write(json.dumps({"ok": False, "error": message},
                                ensure_ascii=True) + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Read a local .xlsx/.csv/.docx file with stdlib only.")
    ap.add_argument("path", nargs="?", help="path to .xlsx, .csv/.tsv or .docx")
    ap.add_argument("--sheet", help="sheet name or index (default: first visible)")
    ap.add_argument("--all-sheets", action="store_true")
    ap.add_argument("--no-header", action="store_true", help="treat row 1 as data")
    ap.add_argument("--max-rows", type=int, default=0, help="cap rows read (0 = all)")
    ap.add_argument("--format", choices=["json", "jsonl", "csv", "md"],
                    default="json")
    ap.add_argument("--output", help="write to this file instead of stdout")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.path:
        ap.error("path is required unless --selftest")

    try:
        result = to_result(args.path, args.all_sheets, args.sheet,
                           not args.no_header, args.max_rows)
    except (OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        emit_error("cannot read %s: %s" % (args.path, exc))
        return 2

    if result.get("kind") == "docx" and args.format == "csv":
        emit_error(".docx has no tabular output; use --format json or md")
        return 2

    if args.format == "json":
        text = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.format == "jsonl":
        if result.get("kind") == "docx":
            text = "\n".join(json.dumps(b, ensure_ascii=False)
                             for b in result["blocks"])
        else:
            combined = []
            if "all_sheets" in result:
                for s in result["all_sheets"]:
                    combined.extend(s["rows"])
            else:
                combined = result["rows"]
            text = "\n".join(json.dumps(r, ensure_ascii=False) for r in combined)
    elif args.format == "md":
        if result.get("kind") == "docx":
            text = blocks_to_markdown(result["blocks"])
        elif result.get("kind") == "delimited":
            text = rows_to_markdown(result.get("header"), result.get("rows") or [])
        elif "all_sheets" in result:
            text = "\n\n".join(
                "### %s\n\n%s" % (s["sheet"],
                                  rows_to_markdown(s.get("header"), s.get("rows") or []))
                for s in result["all_sheets"])
        else:
            text = rows_to_markdown(result.get("header"), result.get("rows") or [])
    else:  # csv
        buf = io.StringIO()
        w = csv.writer(buf)
        if result.get("header"):
            w.writerow(result["header"])
        if "all_sheets" in result:
            for s in result["all_sheets"]:
                for r in s["rows"]:
                    w.writerow(["" if v is None else v for v in r])
        else:
            for r in result["rows"]:
                w.writerow(["" if v is None else v for v in r])
        text = buf.getvalue()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.output)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
