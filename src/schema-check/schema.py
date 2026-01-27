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




