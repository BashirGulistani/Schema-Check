from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .schema import infer_schema
from .diff import diff_schemas
from .report import to_payload, write_json, write_html






