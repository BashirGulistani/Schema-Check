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



@dataclass(frozen=True)
class DriftReport:
    changes: List[Change]
    breaking: bool
    risk_score: int  





def _severity_for(change_kind: str, before: FieldSchema | None, after: FieldSchema | None) -> tuple[str, str]:
    if change_kind == "removed":
        return "high", "Field removed. Downstream queries may fail."
    if change_kind == "added":
        return "low", "Field added. Usually safe unless strict schemas are enforced."
    if change_kind == "type_changed":
        if before and after:
            if before.type == "string" and after.type in {"int", "float", "bool"}:
                return "medium", "Type narrowed (string -> numeric/bool). Might break free-form values."
            if before.type in {"int", "float"} and after.type == "string":
                return "medium", "Type widened (numeric -> string). Usually safe but may break numeric ops."
            if (before.type, after.type) in {("int", "float"), ("float", "int")}:
                return "medium", "Numeric type changed. Watch for rounding/casts."
            return "high", "Type changed. Treat as breaking until verified."
        return "high", "Type changed."
    if change_kind == "nullability_changed":
        if before and after:
            if before.nullable is False and after.nullable is True:
                return "medium", "Field became nullable. Downstream non-null assumptions may break."
            if before.nullable is True and after.nullable is False:
                return "low", "Field became non-null. Usually fine."
        return "medium", "Nullability changed."
    if change_kind == "presence_changed":
        return "medium", "Field presence changed across records (JSON variability)."
    return "low", "Change detected."




