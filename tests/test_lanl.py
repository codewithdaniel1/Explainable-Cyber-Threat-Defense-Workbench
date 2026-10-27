from __future__ import annotations

import csv
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ctdw.lanl import (  # noqa: E402
    AuthEvent,
    build_feature_rows,
    prepare_auth_features,
    read_auth_events,
)


def event(time: int, user: str, source: str, destination: str, result="Success") -> AuthEvent:
    return AuthEvent(time, user, user, source, destination, "Negotiate", "Network", "LogOn", result)


class PastOnlyFeaturesTest(unittest.TestCase):
    def test_same_second_events_do_not_see_each_other(self) -> None:
        first = event(10, "U1@DOM1", "C1", "C2", "Failure")
        second = event(10, "U1@DOM1", "C1", "C3")
        later = event(11, "U1@DOM1", "C1", "C2")
        rows = list(build_feature_rows(iter([first, second, later]), {later.redteam_key}))

        self.assertEqual([r["user_prior_events"] for r in rows], [0, 0, 2])
        self.assertEqual([r["user_prior_failures"] for r in rows], [0, 0, 1])
        self.assertEqual([r["user_prior_distinct_destinations"] for r in rows], [0, 0, 2])
        self.assertEqual([r["known_redteam_event"] for r in rows], [0, 0, 1])
        self.assertEqual(rows[2]["user_destination_prior_events"], 1)

    def test_out_of_order_events_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "ordered"):
            list(build_feature_rows(iter([event(11, "U1", "C1", "C2"), event(10, "U1", "C1", "C2")]), set()))

    def test_preparation_manifest_reports_label_coverage_and_cap(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            auth = root / "auth.txt.gz"
            redteam = root / "redteam.txt.gz"
            output = root / "auth_features.csv.gz"
            with gzip.open(auth, "wt", encoding="utf-8") as stream:
                stream.write("1,U1@DOM1,U1@DOM1,C1,C2,Negotiate,Network,LogOn,Success\n")
                stream.write("2,U1@DOM1,U1@DOM1,C1,C3,Negotiate,Network,LogOn,Success\n")
            with gzip.open(redteam, "wt", encoding="utf-8") as stream:
                stream.write("2,U1@DOM1,C1,C3\n")
                stream.write("3,U9@DOM1,C1,C9\n")

            manifest = prepare_auth_features(auth, redteam, output, max_events=2)
            self.assertEqual(manifest["rows_written"], 2)
            self.assertEqual(manifest["known_redteam_rows"], 1)
            self.assertEqual(manifest["redteam_keys_total"], 2)
            self.assertEqual(manifest["redteam_keys_matched"], 1)
            self.assertTrue(manifest["is_capped_run"])
            with gzip.open(output, "rt", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1]["known_redteam_event"], "1")
            self.assertEqual(
                json.loads((root / "auth_features.csv.manifest.json").read_text())["rows_written"],
                2,
            )

    def test_malformed_auth_row_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            auth = Path(temp) / "auth.txt"
            auth.write_text("1,U1,C1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected 9"):
                list(read_auth_events(auth))


if __name__ == "__main__":
    unittest.main()
