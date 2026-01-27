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







def _score_change(severity: str) -> int:
    return {"low": 5, "medium": 15, "high": 35}.get(severity, 10)

def diff_schemas(before: DatasetSchema, after: DatasetSchema) -> DriftReport:
    changes: List[Change] = []

    b_fields = before.fields
    a_fields = after.fields

    b_set = set(b_fields.keys())
    a_set = set(a_fields.keys())

    for f in sorted(a_set - b_set):
        sev, note = _severity_for("added", None, a_fields[f])
        changes.append(Change("added", f, None, a_fields[f].type, sev, note))

    for f in sorted(b_set - a_set):
        sev, note = _severity_for("removed", b_fields[f], None)
        changes.append(Change("removed", f, b_fields[f].type, None, sev, note))

    for f in sorted(b_set & a_set):
        bf = b_fields[f]
        af = a_fields[f]

        if bf.type != af.type:
            sev, note = _severity_for("type_changed", bf, af)
            changes.append(Change("type_changed", f, bf.type, af.type, sev, note))

        if bf.nullable != af.nullable:
            sev, note = _severity_for("nullability_changed", bf, af)
            changes.append(Change("nullability_changed", f, str(bf.nullable), str(af.nullable), sev, note))

        if abs(bf.presence - af.presence) >= 0.2: 
            sev, note = _severity_for("presence_changed", bf, af)
            changes.append(Change(
                "presence_changed",
                f,
                f"{bf.presence:.2f}",
                f"{af.presence:.2f}",
                sev,
                note
            ))

    score = sum(_score_change(c.severity) for c in changes)
    score = min(100, score)

    breaking = any(c.severity == "high" or c.kind == "removed" for c in changes)
    return DriftReport(changes=changes, breaking=breaking, risk_score=score)



