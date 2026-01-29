# Schema Check

Schema check is a small tool I wanted *every* time a vendor feed randomly changed and quietly broke a pipeline.


It compares two snapshots of a dataset (CSV / JSONL / JSON), infers a lightweight schema from samples,
then tells you what drifted:
- new fields
- removed fields
- type changes (int → float, string → int, etc.)
- nullability changes
- (for JSON) “presence drift” when a field suddenly stops appearing in most records

It also produces a risk score so you can use it as a CI gate if you want.

This is not meant to be a full data profiling suite. It’s a “stop the bleed” tool: catch drift early, explain it clearly.

---

## Install

From source:

```bash
pip install -e .
