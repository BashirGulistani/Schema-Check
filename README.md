# Schema Check

Schema check is a small tool I wanted *every* time a vendor feed randomly changed and quietly broke a pipeline.


It compares two snapshots of a dataset (CSV / JSONL / JSON), infers a lightweight schema from samples,
then tells you what drifted:
- new fields
- removed fields
