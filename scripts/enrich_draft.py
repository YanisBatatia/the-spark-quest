"""Add initial browsing metadata to imported records.

These values support the first working UI and remain marked needs-review.
Run once on raw imports; the script leaves records that already have moods alone.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


RECORDS = Path(__file__).resolve().parents[1] / "src" / "data" / "experiences"


def ids(spec: str) -> set[str]:
    result: set[str] = set()
    for chunk in spec.split():
        if "-" in chunk:
            first, last = map(int, chunk.split("-", 1))
            result.update(f"{number:03d}" for number in range(first, last + 1))
        else:
            result.add(chunk.zfill(3))
    return result


MOODS = {
    "wonder": ids("001 002 006 009 015 016 019 020 025 031 032 033 034 035 036 037 039 041 043-050 081-090 093 096-100 102"),
    "make": ids("061-068 071"),
    "listen": ids("041-044 050-060 089 090 097 110"),
    "taste": ids("014 040 070 071 073 074 077-080"),
    "nature": ids("001-018 021-039 069 091 092 094 095 102"),
    "rest": ids("001 003 005 010 012 014 017 018 026 030 034-036 051 075 076 079 091 092 102 110"),
}

CUSTOM_TEASERS = {
    "003": "Watch snowy wilderness pass from a warm carriage.",
    "021": "See gentle giants from a waterside boardwalk.",
    "051": "Spend an intimate evening listening to live New Orleans jazz.",
    "067": "Make something new with a local Santa Fe artist.",
}

for path in sorted(RECORDS.glob("*.json")):
    data = json.loads(path.read_text())
    if "moods" in data:
        continue
    entry_id = data["id"]
    first_sentence = re.split(r"(?<=[.!?])\s+", data["description"], maxsplit=1)[0]
    data["teaser"] = CUSTOM_TEASERS.get(entry_id, first_sentence)
    data["moods"] = [mood for mood, matches in MOODS.items() if entry_id in matches]
    if not data["moods"]:
        raise ValueError(f"No mood for {entry_id}")
    data["location"]["placeGroup"] = data["location"]["label"].split(",")[-1].strip()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

print("Added initial teasers, mood tags, and place groups to 101 records.")
