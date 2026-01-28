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


    summary = payload.get("summary", {})
    changes = payload.get("changes", [])

    # small, readable report
    rows = []
    for c in changes:
        rows.append(
            f"<tr>"
            f"<td><code>{h(c.get('kind'))}</code></td>"
            f"<td><code>{h(c.get('field'))}</code></td>"
            f"<td><code>{h(c.get('before'))}</code></td>"
            f"<td><code>{h(c.get('after'))}</code></td>"
            f"<td>{h(c.get('severity'))}</td>"
            f"<td class='muted'>{h(c.get('note'))}</td>"
            f"</tr>"
        )

    html_text = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>DriftFence Report</title>
<style>
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; background: #0b0b0b; color: #eee; }}
  .card {{ background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); border-radius: 14px; padding: 14px; margin: 12px 0; }}
  h1 {{ margin: 0 0 6px; font-size: 22px; }}
  .muted {{ color: #b9b9b9; font-size: 13px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border-bottom: 1px solid rgba(255,255,255,.08); padding: 10px; vertical-align: top; font-size: 13px; }}
  th {{ text-align: left; color: #ddd; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
  .pill {{ display:inline-block; padding: 4px 8px; border-radius: 999px; border:1px solid rgba(255,255,255,.16); font-size: 12px; }}
</style>
</head>
<body>
  <h1>DriftFence</h1>
  <div class="muted">Schema drift report</div>

  <div class="card">
    <div><span class="pill">breaking</span> {h(summary.get("breaking"))}</div>
    <div><span class="pill">risk score</span> {h(summary.get("risk_score"))} / 100</div>
    <div><span class="pill">changes</span> {h(summary.get("change_count"))}</div>
  </div>

  <div class="card">
    <h2 style="margin:0 0 10px;font-size:16px;">Changes</h2>
    <table>
      <thead>
        <tr>
          <th>kind</th>
          <th>field</th>
          <th>before</th>
          <th>after</th>
          <th>severity</th>
          <th>notes</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows) if rows else '<tr><td colspan="6" class="muted">No changes detected.</td></tr>'}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
    p.write_text(html_text, encoding="utf-8")








