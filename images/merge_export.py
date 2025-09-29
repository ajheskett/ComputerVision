#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, os, datetime as _dt
from pathlib import Path
import nbformat
from nbconvert import HTMLExporter

def _mk_title_cell(title, author, date_str):
    lines = ["# " + title]
    meta = []
    if author:
        meta.append(f"**Author:** {author}")
    if date_str:
        meta.append(f"**Date:** {date_str}")
    if meta:
        lines.append("")
        lines.extend(meta)
    return nbformat.v4.new_markdown_cell("\n".join(lines))

def _mk_section_cell(name):
    return nbformat.v4.new_markdown_cell(f"# {name}")

def merge_notebooks(paths, add_section_headers=True):
    nb_out = nbformat.v4.new_notebook()
    nb_out.cells = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        if add_section_headers:
            nb_out.cells.append(_mk_section_cell(Path(p).stem))
        nb_out.cells.extend(nb.cells)
    return nb_out

def main():
    ap = argparse.ArgumentParser(description="Merge notebooks → single HTML (no code shown), using built-in template.")
    ap.add_argument("notebooks", nargs="+", help="Input .ipynb files in the desired order")
    ap.add_argument("-o", "--output", default="report.html", help="Output HTML path (default: report.html)")
    ap.add_argument("--title", default="Project Report", help="Report title")
    ap.add_argument("--author", default="", help="Author name")
    ap.add_argument("--date", default="", help="Date string (default: today)")
    ap.add_argument("--no-section-headers", action="store_true", help="Do not insert per-notebook section headers")
    ap.add_argument("--styles", default="styles.css", help="Extra CSS file to embed if present (default: styles.css)")
    ap.add_argument("--base-template", default="classic", choices=["classic","lab"], help="Built-in nbconvert base template (default: classic)")
    args = ap.parse_args()

    for p in args.notebooks:
        if not os.path.exists(p):
            ap.error(f"Input not found: {p}")

    date_str = args.date.strip() or _dt.date.today().isoformat()
    merged = merge_notebooks(args.notebooks, add_section_headers=(not args.no_section_headers))
    merged.cells.insert(0, _mk_title_cell(args.title, args.author, date_str))

    exporter = HTMLExporter()
    exporter.template_name = args.base_template   # use built-in template; no external tpl file needed
    exporter.exclude_input = True                 # hide code cells

    resources = {}
    css_text = ""
    if args.styles and os.path.exists(args.styles):
        with open(args.styles, "r", encoding="utf-8") as f:
            css_text = f.read()
    resources["inlining"] = {"css": [css_text]}

    body, resources = exporter.from_notebook_node(merged, resources=resources)
    Path(args.output).write_text(body, encoding="utf-8")
    print(f"Wrote {Path(args.output).resolve()}")

if __name__ == "__main__":
    main()