import unittest
from driftfence.schema import DatasetSchema, FieldSchema
from driftfence.diff import diff_schemas


class TestDiff(unittest.TestCase):
    def test_added_removed_type_change(self):
        before = DatasetSchema(
            format="csv",
            sampled_rows=10,
            fields={
                "a": FieldSchema("a", "int", False, [], 1.0),
                "b": FieldSchema("b", "string", True, [], 1.0),
            },
        )
        after = DatasetSchema(
            format="csv",
            sampled_rows=10,
            fields={
                "a": FieldSchema("a", "float", False, [], 1.0),  
                "c": FieldSchema("c", "string", True, [], 1.0), 
            },
        )

        rep = diff_schemas(before, after)
        kinds = [c.kind for c in rep.changes]
        self.assertIn("type_changed", kinds)
        self.assertIn("added", kinds)
        self.assertIn("removed", kinds)


if __name__ == "__main__":
    unittest.main()
