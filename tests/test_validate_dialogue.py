import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import validate_dialogue

from validate_dialogue import DIALOGUE_DIR, SCHEMA_PATH, load_schema, validate_graph


class DialogueValidationTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema(SCHEMA_PATH)
        self.graph = json.loads((DIALOGUE_DIR / "keeper_intro.json").read_text())
        self.entries = self.schema["entries"]["keeper_intro.json"]

    def errors(self, graph):
        return validate_graph(graph, self.entries, self.schema)[0]

    def test_real_graph_and_replay_choices(self):
        self.assertEqual([], self.errors(self.graph))
        choices = self.graph["logbook_choice1"]["choices"]
        for first, second in ((0, 1), (1, 0)):
            flags = {}
            flags.update(choices[first]["set_flag"])
            flags.update(choices[second]["set_flag"])
            self.assertEqual(second == 0, flags["skeptic"])
            self.assertEqual(second == 1, flags["believer"])
            self.assertNotEqual(flags["skeptic"], flags["believer"])
            # Save/load preserves the chosen values.
            self.assertEqual(flags, json.loads(json.dumps(flags)))

    def test_unknown_and_malformed_flags(self):
        graph = copy.deepcopy(self.graph)
        graph["logbook_choice1"]["choices"][0]["set_flag"]["skeptik"] = True
        self.assertTrue(any("unknown flag" in e for e in self.errors(graph)))
        graph["logbook_choice1"]["choices"][0]["set_flag"] = {"skeptic": "true"}
        errors = self.errors(graph)
        self.assertTrue(any("boolean" in e for e in errors))
        self.assertTrue(any("assign every" in e for e in errors))

    def test_conflicting_exclusive_flags(self):
        graph = copy.deepcopy(self.graph)
        graph["logbook_choice1"]["choices"][0]["set_flag"] = {"skeptic": True, "believer": True}
        self.assertTrue(any("at most one true" in e for e in self.errors(graph)))

    def test_missing_target_and_entry(self):
        graph = copy.deepcopy(self.graph)
        graph["logbook"]["next"] = "missing"
        self.assertTrue(any("missing node" in e for e in self.errors(graph)))
        self.assertTrue(any("missing entry" in e for e in validate_graph(graph, ["absent"], self.schema)[0]))

    def test_unreachable_and_trapped_cycle(self):
        graph = copy.deepcopy(self.graph)
        graph["orphan"] = {"next": None}
        self.assertTrue(any("unreachable" in e for e in self.errors(graph)))
        graph["logbook"]["next"] = "logbook"
        self.assertTrue(any("no path to a terminal" in e for e in self.errors(graph)))

    def test_malformed_nodes_and_choices_are_reported(self):
        graph = copy.deepcopy(self.graph)
        graph["logbook_choice1"]["choices"] = [3, {"text": "x", "next": 9}]
        errors = self.errors(graph)
        self.assertTrue(any("must be an object" in e for e in errors))
        self.assertTrue(any("node ID or null" in e for e in errors))

    def test_invalid_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "schema.json"
            path.write_text('{"flags": {"x": "number"}, "entries": {}, "exclusive_flag_groups": []}')
            with self.assertRaises(ValueError):
                load_schema(path)

    def test_old_spec_fields_are_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph["logbook_choice1"]["choices"][0]["set"] = "skeptic"
        self.assertTrue(any("unsupported field" in e for e in self.errors(graph)))

    def test_invalid_json_returns_failure_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "bad.json").write_text("{")
            schema = copy.deepcopy(self.schema)
            schema["entries"] = {"bad.json": ["start"]}
            schema_path = folder / "schema.json"
            schema_path.write_text(json.dumps(schema))
            with patch.object(validate_dialogue, "SCHEMA_PATH", schema_path), patch.object(validate_dialogue, "DIALOGUE_DIR", folder):
                # The schema is outside the graphs directory in production.
                graph_folder = folder / "graphs"
                graph_folder.mkdir()
                (folder / "bad.json").rename(graph_folder / "bad.json")
                with patch.object(validate_dialogue, "DIALOGUE_DIR", graph_folder):
                    self.assertEqual(1, validate_dialogue.main())


if __name__ == "__main__":
    unittest.main()
