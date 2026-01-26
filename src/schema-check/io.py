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






