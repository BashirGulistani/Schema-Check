from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
import re

from .io import read_rows


_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$")





def _is_null(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        s = v.strip()
        return s == "" or s.lower() in {"null", "none", "na", "n/a"}
    return False



def _as_str(v: Any) -> str:
    return v if isinstance(v, str) else str(v)


def _infer_scalar_type(v: Any) -> str:
    if _is_null(v):
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int) and not isinstance(v, bool):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, dict):
        return "object"
    if isinstance(v, list):
        return "array"

    s = _as_str(v).strip()
    sl = s.lower()

    if sl in {"true", "false"}:
        return "bool"
    if _INT_RE.match(s):
        return "int"
    if _FLOAT_RE.match(s):
        return "float"
    return "string"





def _merge_types(types: Set[str]) -> str:
    t = set(types)
    t.discard("null")
    if not t:
        return "null"
    if "object" in t:
        return "object"
    if "array" in t:
        return "array"
    if "string" in t:
        return "string"
    if "float" in t and "int" in t:
        return "float"
    if "float" in t:
        return "float"
    if "int" in t:
        return "int"
    if "bool" in t:
        return "bool"
    return "string"


@dataclass(frozen=True)
class FieldSchema:
    name: str
    type: str
    nullable: bool
    examples: List[str] = field(default_factory=list)
    presence: float = 1.0


@dataclass(frozen=True)
class DatasetSchema:
    format: str
    fields: Dict[str, FieldSchema]
    sampled_rows: int



def infer_schema(path: str, *, max_rows: int = 5000, max_examples: int = 3) -> DatasetSchema:
    rows_iter = read_rows(path, max_rows=max_rows)

    type_buckets: Dict[str, Set[str]] = {}
    nullables: Dict[str, bool] = {}
    examples: Dict[str, List[str]] = {}
    present_counts: Dict[str, int] = {}
    total = 0

    for row in rows_iter:
        total += 1
        keys = set(row.keys())

        for k in keys:
            present_counts[k] = present_counts.get(k, 0) + 1

        for k, v in row.items():
            if k not in type_buckets:
                type_buckets[k] = set()
                nullables[k] = False
                examples[k] = []

            t = _infer_scalar_type(v)
            type_buckets[k].add(t)
            if t == "null":
                nullables[k] = True

            if len(examples[k]) < max_examples and not _is_null(v):
                examples[k].append(_as_str(v)[:80])

    from .io import sniff_format
    fmt = sniff_format(path)

    fields: Dict[str, FieldSchema] = {}
    for k in sorted(type_buckets.keys()):
        merged = _merge_types(type_buckets[k])
        presence = (present_counts.get(k, 0) / total) if total else 0.0
        fields[k] = FieldSchema(
            name=k,
            type=merged,
            nullable=bool(nullables.get(k, False)),
            examples=examples.get(k, []),
            presence=presence,
        )

    return DatasetSchema(format=fmt, fields=fields, sampled_rows=total)



