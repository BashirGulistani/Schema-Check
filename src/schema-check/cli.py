from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .schema import infer_schema
from .diff import diff_schemas
from .report import to_payload, write_json, write_html





def main() -> None:
    ap = argparse.ArgumentParser(
        prog="driftfence",
        description="Detect schema drift in CSV/JSONL/JSON files and generate JSON + HTML reports.",
    )
    ap.add_argument("before", help="Path to baseline file (older snapshot)")
    ap.add_argument("after", help="Path to new file (latest snapshot)")
    ap.add_argument("--max-rows", type=int, default=5000, help="Max rows to sample (default: 5000)")
    ap.add_argument("--out-dir", default=".driftfence-out", help="Output directory (default: .driftfence-out)")
    ap.add_argument("--fail-on-breaking", action="store_true", help="Exit non-zero if breaking drift detected")
    ap.add_argument("--fail-risk", type=int, default=None, help="Exit non-zero if risk score >= N (0..100)")
    args = ap.parse_args()







