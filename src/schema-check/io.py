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







