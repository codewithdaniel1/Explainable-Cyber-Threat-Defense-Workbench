"""Stream LANL authentication events into past-only research features.

The LANL red-team file names known compromise events. Unmatched authentication
events are unlabeled, not confirmed benign. Keep that distinction in downstream
analysis and reporting.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, TextIO


AUTH_COLUMNS = (
    "time",
    "source_user",
    "destination_user",
    "source_computer",
    "destination_computer",
    "authentication_type",
    "logon_type",
    "orientation",
    "result",
)

FEATURE_COLUMNS = (
    *AUTH_COLUMNS,
    "day",
    "same_computer",
    "user_prior_events",
    "user_prior_failures",
    "user_destination_prior_events",
    "source_destination_prior_events",
    "user_prior_distinct_destinations",
    "destination_prior_events",
    "known_redteam_event",
)


@dataclass(frozen=True)
class AuthEvent:
    time: int
    source_user: str
    destination_user: str
    source_computer: str
    destination_computer: str
    authentication_type: str
    logon_type: str
    orientation: str
    result: str

    @property
    def redteam_key(self) -> tuple[int, str, str, str]:
        return (
            self.time,
            self.source_user,
            self.source_computer,
            self.destination_computer,
        )


def _open_text(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8", newline="")


def read_redteam_keys(path: Path) -> set[tuple[int, str, str, str]]:
    """Return exact event keys from LANL's redteam.txt[.gz]."""
    keys: set[tuple[int, str, str, str]] = set()
    with _open_text(path) as stream:
        for line_number, row in enumerate(csv.reader(stream), start=1):
            if len(row) != 4:
                raise ValueError(f"Red-team line {line_number} has {len(row)} fields, expected 4")
            keys.add((int(row[0]), row[1], row[2], row[3]))
    return keys


def read_auth_events(path: Path) -> Iterator[AuthEvent]:
    """Parse LANL auth.txt[.gz] without loading the source into memory."""
    with _open_text(path) as stream:
        for line_number, row in enumerate(csv.reader(stream), start=1):
            if len(row) != len(AUTH_COLUMNS):
                raise ValueError(
                    f"Authentication line {line_number} has {len(row)} fields, "
                    f"expected {len(AUTH_COLUMNS)}"
                )
            yield AuthEvent(int(row[0]), *row[1:])


def _timestamp_groups(events: Iterator[AuthEvent]) -> Iterator[list[AuthEvent]]:
    """Group simultaneous events so none contributes to another's history."""
    group: list[AuthEvent] = []
    previous_time: int | None = None
    for event in events:
        if previous_time is not None and event.time < previous_time:
            raise ValueError("Authentication input must be ordered by nondecreasing time")
        if group and event.time != previous_time:
            yield group
            group = []
        group.append(event)
        previous_time = event.time
    if group:
        yield group


def build_feature_rows(
    events: Iterator[AuthEvent], redteam_keys: set[tuple[int, str, str, str]]
) -> Iterator[dict[str, object]]:
    """Yield event features using only strictly earlier timestamps.

    Counts describe all prior authentication attempts. The raw user/computer IDs
    support history and auditing; the eventual classifier will omit them.
    """
    user_events: Counter[str] = Counter()
    user_failures: Counter[str] = Counter()
    user_destination: Counter[tuple[str, str]] = Counter()
    source_destination: Counter[tuple[str, str]] = Counter()
    destination_events: Counter[str] = Counter()
    user_distinct_destinations: Counter[str] = Counter()

    for group in _timestamp_groups(events):
        for event in group:
            user = event.source_user
            source = event.source_computer
            destination = event.destination_computer
            yield {
                **asdict(event),
                "day": event.time // 86400,
                "same_computer": int(source == destination),
                "user_prior_events": user_events[user],
                "user_prior_failures": user_failures[user],
                "user_destination_prior_events": user_destination[(user, destination)],
                "source_destination_prior_events": source_destination[(source, destination)],
                "user_prior_distinct_destinations": user_distinct_destinations[user],
                "destination_prior_events": destination_events[destination],
                "known_redteam_event": int(event.redteam_key in redteam_keys),
            }
        for event in group:
            user = event.source_user
            destination = event.destination_computer
            user_events[user] += 1
            user_failures[user] += int(event.result.lower() == "failure")
            if user_destination[(user, destination)] == 0:
                user_distinct_destinations[user] += 1
            user_destination[(user, destination)] += 1
            source_destination[(event.source_computer, destination)] += 1
            destination_events[destination] += 1


def prepare_auth_features(
    auth_path: Path,
    redteam_path: Path,
    output_path: Path,
    *,
    max_day: int | None = None,
    max_events: int | None = None,
) -> dict[str, object]:
    """Write compressed feature rows and a provenance/coverage manifest.

    Limits apply to the beginning of the ordered stream. A capped run is for
    development; it must never be presented as a full-dataset evaluation.
    """
    if max_day is not None and max_day < 0:
        raise ValueError("max_day must be nonnegative")
    if max_events is not None and max_events < 1:
        raise ValueError("max_events must be positive")

    redteam_keys = read_redteam_keys(redteam_path)
    matched_keys: set[tuple[int, str, str, str]] = set()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    def selected_events() -> Iterator[AuthEvent]:
        for index, event in enumerate(read_auth_events(auth_path)):
            if max_events is not None and index >= max_events:
                break
            if max_day is not None and event.time // 86400 > max_day:
                break
            yield event

    row_count = 0
    positive_rows = 0
    max_observed_day: int | None = None
    with gzip.open(output_path, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FEATURE_COLUMNS)
        writer.writeheader()
        for row in build_feature_rows(selected_events(), redteam_keys):
            writer.writerow(row)
            row_count += 1
            positive_rows += int(row["known_redteam_event"])
            max_observed_day = int(row["day"])
            if row["known_redteam_event"]:
                matched_keys.add(
                    (
                        int(row["time"]),
                        str(row["source_user"]),
                        str(row["source_computer"]),
                        str(row["destination_computer"]),
                    )
                )

    manifest = {
        "auth_source": str(auth_path.resolve()),
        "redteam_source": str(redteam_path.resolve()),
        "output": str(output_path.resolve()),
        "rows_written": row_count,
        "known_redteam_rows": positive_rows,
        "redteam_keys_total": len(redteam_keys),
        "redteam_keys_matched": len(matched_keys),
        "max_observed_day": max_observed_day,
        "max_day_limit": max_day,
        "max_events_limit": max_events,
        "is_capped_run": max_day is not None or max_events is not None,
        "label_warning": "Other events are unlabeled, not confirmed benign.",
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

