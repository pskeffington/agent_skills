import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_toolset.journal import Journal, JournalError

class JournalTests(unittest.TestCase):
    def test_append_restart_replay_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "events.jsonl"
            journal = Journal(path)
            a = journal.append("F2-journal", "TASK_CREATED", {"status": "queued"})
            b = Journal(path).append("F2-journal", "TASK_READY", {"status": "ready"})
            replay = Journal(path).replay()
            self.assertEqual([1, 2], [e["sequence"] for e in replay])
            self.assertEqual(a["hash"], b["previous_hash"])
            checkpoint = Journal(path).checkpoint(pathlib.Path(tmp) / "checkpoint.json")
            self.assertEqual(2, json.loads(checkpoint.read_text())["sequence"])

    def test_tamper_and_sequence_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "events.jsonl"
            Journal(path).append("F2-journal", "TASK_CREATED", {"status": "queued"})
            record = json.loads(path.read_text())
            record["payload"]["status"] = "done"
            path.write_text(json.dumps(record) + "\n")
            with self.assertRaises(JournalError):
                Journal(path).replay()

    def test_incomplete_tail_is_ignored_and_next_append_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "events.jsonl"
            journal = Journal(path)
            first = journal.append("F2-journal", "TASK_CREATED", {"status": "queued"})
            with path.open("ab") as stream:
                stream.write(b'{"sequence":2')
            self.assertEqual([first["hash"]], [e["hash"] for e in journal.replay()])
            next_event = journal.append("F2-journal", "TASK_READY", {"status": "ready"})
            self.assertEqual(2, next_event["sequence"])
            self.assertEqual([1, 2], [e["sequence"] for e in journal.replay()])

if __name__ == "__main__":
    unittest.main()
