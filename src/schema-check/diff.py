from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .schema import DatasetSchema, FieldSchema


@dataclass(frozen=True)
class Change:
    kind: str 
    field: str
    before: str | None
    after: str | None
    severity: str  
    note: str



