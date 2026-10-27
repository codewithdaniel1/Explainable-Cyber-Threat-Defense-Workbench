"""Prepare event-level LANL authentication features for the research notebook."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ctdw.lanl import prepare_auth_features  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auth", required=True, type=Path, help="auth.txt.gz from LANL")
    parser.add_argument("--redteam", required=True, type=Path, help="redteam.txt.gz from LANL")
    parser.add_argument(
        "--output",
        default=Path("data/processed/auth_features.csv.gz"),
        type=Path,
    )
    parser.add_argument("--max-day", type=int, help="Inclusive LANL day for a development run")
    parser.add_argument("--max-events", type=int, help="Event cap for a development run")
    args = parser.parse_args()
    manifest = prepare_auth_features(
        args.auth, args.redteam, args.output,
        max_day=args.max_day, max_events=args.max_events,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
