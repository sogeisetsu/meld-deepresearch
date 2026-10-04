#!/usr/bin/env python
"""Read a local spreadsheet into JSON/CSV with the Python standard library only.

Intended to be run by the skill when a research task supplies local data files
(`.xlsx`, `.csv`, `.tsv`). The run should record the exact command as an
`observations[]` entry and cite every figure computed from it with `[^oN]`.

Zero third-party dependencies. Handles: sheet mapping via workbook rels (not a
hard-coded `sheet1.xml`), shared strings, inline/formula/boolean/error cells,
sparse cells, and Excel serial dates via `styles.xml` + `date1904`.

Examples:
  python read_table.py data.xlsx --sheet Sheet1
  python read_table.py data.xlsx --all-sheets --format json
  python read_table.py data.csv --max-rows 50
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


def to_result(path, all_sheets, sheet_sel, header, max_rows):
    name = path
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
    print("read_table selftest: OK (sheets, shared/inline strings, number, boolean, date, sparse)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Read a local .xlsx/.csv table with stdlib only.")
    ap.add_argument("path", nargs="?", help="path to .xlsx or .csv")
    ap.add_argument("--sheet", help="sheet name or index (default: first visible)")
    ap.add_argument("--all-sheets", action="store_true")
    ap.add_argument("--no-header", action="store_true", help="treat row 1 as data")
    ap.add_argument("--max-rows", type=int, default=0, help="cap rows read (0 = all)")
    ap.add_argument("--format", choices=["json", "jsonl", "csv"], default="json")
    ap.add_argument("--output", help="write to this file instead of stdout")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.path:
        ap.error("path is required unless --selftest")

    result = to_result(args.path, args.all_sheets, args.sheet, not args.no_header, args.max_rows)

    if args.format == "json":
        text = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.format == "jsonl":
        combined = []
        if "all_sheets" in result:
            for s in result["all_sheets"]:
                combined.extend(s["rows"])
        else:
            combined = result["rows"]
        text = "\n".join(json.dumps(r, ensure_ascii=False) for r in combined)
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
