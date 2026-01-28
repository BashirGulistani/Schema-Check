from __future__ import annotations
import html
import json
from pathlib import Path
from typing import Any, Dict

from .schema import DatasetSchema
from .diff import DriftReport


def write_json(path: str, payload: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")







def to_payload(before: DatasetSchema, after: DatasetSchema, report: DriftReport) -> dict:
    def pack_schema(s: DatasetSchema) -> dict:
        return {
            "format": s.format,
            "sampled_rows": s.sampled_rows,
            "fields": {
                k: {
                    "type": f.type,
                    "nullable": f.nullable,
                    "presence": round(f.presence, 4),
                    "examples": f.examples,
                }
                for k, f in s.fields.items()
            }
        }




    return {
        "summary": {
            "breaking": report.breaking,
            "risk_score": report.risk_score,
            "change_count": len(report.changes),
        },
        "changes": [
            {
                "kind": c.kind,
                "field": c.field,
                "before": c.before,
                "after": c.after,
                "severity": c.severity,
                "note": c.note,
            }
            for c in report.changes
        ],
        "before": pack_schema(before),
        "after": pack_schema(after),
    }


def write_html(path: str, payload: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    def h(x: Any) -> str:
        return html.escape("" if x is None else str(x))











