#!/usr/bin/env python3
"""Repair Marrow structured-table rendering without changing source data.

The canonical ED8 bundles store table columns as objects (``{key,label}``) and
rows as keyed objects. The original Marrow UI renderer was written for the
older presentation shape of string columns + positional row arrays. Passing the
canonical source shape directly to that renderer turns column objects into the
literal string ``[object Object]`` and produces empty cells.

This deterministic post-transform keeps the existing table UI/CSS, normalizes
only the presentation input, and audits the source table contract before the
app is packaged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
MARKER = "NK_MARROW_STRUCTURED_TABLE_RENDERER_V1"

source = HTML.read_text(encoding="utf-8")
if MARKER in source:
    raise SystemExit("Marrow structured-table renderer already installed")

# Fail closed if this is run before the Marrow bank transformer or after the
# explanation architecture has unexpectedly changed.
if "function nkRenderMarrowTable(" not in source:
    raise SystemExit("Base Marrow table renderer missing")
if "const NK_MARROW_EXPLANATION_GOLD_V1=" not in source:
    raise SystemExit("Marrow explanation gold wrapper missing")

# Audit the generated canonical source payload itself. This distinguishes a
# source-data defect from a renderer defect and prevents empty source tables
# from being hidden by a presentation patch.
data_marker = "  const MARROW_DATA = "
if source.count(data_marker) != 1:
    raise SystemExit(f"Marrow data declaration count: {source.count(data_marker)}")
data_start = source.index(data_marker) + len(data_marker)
data_end = source.index(";\n", data_start)
try:
    payload = json.loads(source[data_start:data_end])
except Exception as exc:
    raise SystemExit(f"Generated Marrow data JSON is invalid: {exc}") from exc
records = payload.get("records") if isinstance(payload, dict) else None
if not isinstance(records, list) or len(records) != 3:
    raise SystemExit("Canonical Marrow data must contain exactly three subject records")


def _scalar(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value).strip()
    if isinstance(value, list):
        return " · ".join(filter(None, (_scalar(item) for item in value)))
    if isinstance(value, dict):
        for key in ("text", "label", "value", "title", "name", "content"):
            if key in value:
                text = _scalar(value.get(key))
                if text:
                    return text
        return " · ".join(filter(None, (_scalar(item) for item in value.values())))
    return str(value).strip()


def _table_text(table: dict) -> tuple[list[str], list[list[str]]]:
    raw_columns = table.get("columns", [])
    if not isinstance(raw_columns, list):
        return [], []
    columns: list[tuple[str, str]] = []
    for index, column in enumerate(raw_columns):
        if isinstance(column, dict):
            key = str(column.get("key") or column.get("id") or column.get("field") or index)
            label = _scalar(
                column.get("label")
                or column.get("title")
                or column.get("name")
                or column.get("text")
                or column.get("key")
            )
        else:
            key = str(index)
            label = _scalar(column)
        columns.append((key, label or key))

    normalized_rows: list[list[str]] = []
    raw_rows = table.get("rows", [])
    if not isinstance(raw_rows, list):
        return [label for _, label in columns], []
    for row in raw_rows:
        if isinstance(row, list):
            cells = [_scalar(row[i]) if i < len(row) else "" for i in range(len(columns))]
        elif isinstance(row, dict):
            row_cells = row.get("cells")
            if isinstance(row_cells, list):
                by_key: dict[str, object] = {}
                for i, cell in enumerate(row_cells):
                    if isinstance(cell, dict):
                        cell_key = cell.get("key") or cell.get("column") or cell.get("columnKey")
                        if cell_key is not None:
                            by_key[str(cell_key)] = cell
                    by_key.setdefault(str(i), cell)
                cells = []
                for i, (key, _) in enumerate(columns):
                    cell = by_key.get(key, by_key.get(str(i)))
                    if isinstance(cell, dict):
                        cell = (
                            cell.get("value")
                            if "value" in cell
                            else cell.get("text")
                            if "text" in cell
                            else cell.get("content")
                            if "content" in cell
                            else cell.get("label")
                        )
                    cells.append(_scalar(cell))
            else:
                cells = [_scalar(row.get(key)) for key, _ in columns]
        else:
            cells = [_scalar(row)] + [""] * max(0, len(columns) - 1)
        normalized_rows.append(cells)
    return [label for _, label in columns], normalized_rows


table_count = 0
q10_checked = False
subject_counts: dict[str, int] = {}
for record in records:
    subject = str(record.get("subject", ""))
    subject_counts.setdefault(subject, 0)
    for question in record.get("questions", []):
        structured = question.get("structuredExplanation") or {}
        tables = structured.get("tables") or []
        if not isinstance(tables, list):
            raise SystemExit(f"Structured table list invalid: {question.get('id')}")
        for table in tables:
            if not isinstance(table, dict):
                raise SystemExit(f"Structured table object invalid: {question.get('id')}")
            headers, rows = _table_text(table)
            table_id = str(table.get("table_id") or table.get("id") or question.get("id"))
            if not headers or any(not header.strip() for header in headers):
                raise SystemExit(f"Structured table has empty header: {table_id}")
            if not rows or any(not any(cell.strip() for cell in row) for row in rows):
                raise SystemExit(f"Structured table has empty source row: {table_id}")
            if any("[object Object]" in cell for row in rows for cell in row):
                raise SystemExit(f"Structured table source contains object-string leakage: {table_id}")
            table_count += 1
            subject_counts[subject] += 1
            if str(question.get("id")) == "marrow__ANAT_CH05_Q010":
                joined = "\n".join(headers + [cell for row in rows for cell in row])
                for expected in (
                    "Pharyngeal Arch",
                    "Muscle derivatives",
                    "Muscles of mastication",
                    "Larynx - cricothyroid",
                    "All intrinsic muscles (except cricothyroid)",
                ):
                    if expected not in joined:
                        raise SystemExit(f"Anatomy Ch5 Q10 source table missing {expected!r}")
                q10_checked = True

if table_count < 1:
    raise SystemExit("Canonical Marrow corpus unexpectedly contains no structured tables")
if not q10_checked:
    raise SystemExit("Anatomy Ch5 Q10 structured table was not found in generated canonical data")

# Adapt canonical object-keyed tables to the older renderer's presentation
# contract. We intentionally delegate final markup to nkRenderMarrowTable so the
# accepted table card styling remains unchanged.
helper = r'''
  // NK_MARROW_STRUCTURED_TABLE_RENDERER_V1
  function nkMarrowTableCellText(value){
    if(value===null||value===undefined)return '';
    if(Array.isArray(value))return value.map(nkMarrowTableCellText).filter(Boolean).join(' · ');
    if(typeof value==='object'){
      for(const key of ['text','label','value','title','name','content']){
        if(Object.prototype.hasOwnProperty.call(value,key)){
          const nested=nkMarrowTableCellText(value[key]);
          if(nested)return nested;
        }
      }
      return Object.values(value).map(nkMarrowTableCellText).filter(Boolean).join(' · ');
    }
    return String(value).trim();
  }

  function nkNormalizeMarrowStructuredTable(table){
    const sourceTable=(table&&typeof table==='object')?table:{};
    const rawColumns=Array.isArray(sourceTable.columns)?sourceTable.columns:[];
    const columns=rawColumns.map((column,index)=>{
      if(column&&typeof column==='object'&&!Array.isArray(column)){
        const key=String(column.key??column.id??column.field??index);
        const label=nkMarrowTableCellText(column.label??column.title??column.name??column.text??column.key??key)||key;
        return {key,label};
      }
      return {key:String(index),label:nkMarrowTableCellText(column)};
    });
    const rawRows=Array.isArray(sourceTable.rows)?sourceTable.rows:[];
    const rows=rawRows.map(row=>{
      if(Array.isArray(row))return columns.map((_,index)=>nkMarrowTableCellText(row[index]));
      if(row&&typeof row==='object'){
        if(Array.isArray(row.cells)){
          const byKey=new Map();
          row.cells.forEach((cell,index)=>{
            if(cell&&typeof cell==='object'&&!Array.isArray(cell)){
              const key=cell.key??cell.column??cell.columnKey;
              if(key!==undefined&&key!==null)byKey.set(String(key),cell);
            }
            if(!byKey.has(String(index)))byKey.set(String(index),cell);
          });
          return columns.map((column,index)=>{
            let cell=byKey.has(column.key)?byKey.get(column.key):byKey.get(String(index));
            if(cell&&typeof cell==='object'&&!Array.isArray(cell)){
              cell=Object.prototype.hasOwnProperty.call(cell,'value')?cell.value:
                   Object.prototype.hasOwnProperty.call(cell,'text')?cell.text:
                   Object.prototype.hasOwnProperty.call(cell,'content')?cell.content:
                   Object.prototype.hasOwnProperty.call(cell,'label')?cell.label:cell;
            }
            return nkMarrowTableCellText(cell);
          });
        }
        return columns.map(column=>nkMarrowTableCellText(row[column.key]));
      }
      return columns.map((_,index)=>index===0?nkMarrowTableCellText(row):'');
    });
    return {...sourceTable,columns:columns.map(column=>column.label),rows};
  }

  function nkRenderMarrowTableCompat(table){
    return nkRenderMarrowTable(nkNormalizeMarrowStructuredTable(table));
  }
'''

anchor = "  const NK_MARROW_EXPLANATION_GOLD_V1="
if source.count(anchor) != 1:
    raise SystemExit(f"Marrow explanation wrapper anchor count: {source.count(anchor)}")
source = source.replace(anchor, helper + "\n" + anchor, 1)

pattern = re.compile(r"tables\.map\(\s*nkRenderMarrowTable\s*\)\.join\(\s*''\s*\)")
source, call_count = pattern.subn("tables.map(nkRenderMarrowTableCompat).join('')", source)
if call_count != 2:
    raise SystemExit(f"Expected exactly two Marrow table render call sites, found {call_count}")

HTML.write_text(source, encoding="utf-8")
print(
    "MARROW_STRUCTURED_TABLE_RENDERER_OK "
    f"tables={table_count} subjects={subject_counts} call_sites={call_count} q10=verified"
)
