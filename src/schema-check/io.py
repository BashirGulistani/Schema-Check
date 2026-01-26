from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, Iterator, Tuple, Any


def sniff_format(path: str) -> str:
    p = Path(path)
    name = p.name.lower()
    if name.endswith(".jsonl"):
        return "jsonl"
    if name.endswith(".json"):
        return "json"
    return "csv"

def read_csv_rows(path: str, *, max_rows: int = 5000) -> Iterator[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            yield {k: row.get(k) for k in reader.fieldnames or []}


def read_jsonl_rows(path: str, *, max_rows: int = 5000) -> Iterator[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if i >= max_rows:
                break
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if isinstance(obj, dict):
                yield obj


def read_json_rows(path: str, *, max_rows: int = 5000) -> Iterator[Dict[str, Any]]:

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        obj = json.load(f)

    if isinstance(obj, list):
        for i, item in enumerate(obj[:max_rows]):
            if isinstance(item, dict):
                yield item
    elif isinstance(obj, dict):
        for i, item in enumerate(list(obj.values())[:max_rows]):
            if isinstance(item, dict):
                yield item







