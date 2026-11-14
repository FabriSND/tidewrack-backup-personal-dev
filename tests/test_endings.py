import json
import unittest

from validate_dialogue import DIALOGUE_DIR, SCHEMA_PATH, load_schema, validate_graph


class EndingsTests(unittest.TestCase):
    def test_each_ending_reaches_its_own_terminal(self):
        schema = load_schema(SCHEMA_PATH)
        graph = json.loads((DIALOGUE_DIR / "endings.json").read_text())
        entries = schema["entries"]["endings.json"]
        self.assertEqual(
            {"explained_away", "edith_vindicated", "light_believed_edith_doubted", "keep_the_light"},
            set(entries),
        )
        self.assertEqual([], validate_graph(graph, entries, schema)[0])
        visited = set()
        for entry in entries:
            node = entry
            path = set()
            while node is not None:
                self.assertNotIn(node, path, f"{entry} loops at {node}")
                self.assertNotIn(node, visited, f"{entry} shares {node} with another ending")
                path.add(node)
                self.assertTrue(graph[node].get("text"))
                node = graph[node]["next"]
            visited.update(path)
        self.assertEqual(set(graph), visited)


if __name__ == "__main__":
    unittest.main()
