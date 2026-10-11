"""Extract the source catalogue into one JSON record per active experience.

This is a one-time bootstrap, not an editorial rewrite. Rerun only with --force:
later hand-edited records must not be silently overwritten.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "Great_American_Spark_Quest_101_Validated_Experiences.pdf"
OUTPUT = ROOT / "site" / "src" / "data" / "experiences"
EXPECTED_IDS = {
    *(f"{number:03d}" for number in range(1, 72)),
    *(f"{number:03d}" for number in range(73, 101)),
    "102",
    "110",
}
ID_LINE = re.compile(r"(?m)^([0-9]{3})\s*$")


def flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_entry(entry_id: str, block: str, page_number: int) -> dict:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if len(lines) < 4 or not lines[0].startswith(entry_id):
        raise ValueError(f"Malformed entry {entry_id} on page {page_number}")

    title = lines[1]
    location = lines[2]
    rest = "\n".join(lines[3:])
    if rest.count("Practical notes:") != 1:
        raise ValueError(f"Expected one practical note for {entry_id}")

    description, note_section = rest.split("Practical notes:", 1)
    note_section = note_section.split("Open supplied source / booking information", 1)[0]
    return {
        "id": entry_id,
        "title": title,
        "location": {"label": location},
        "description": flatten(description),
        "practicalNoteOriginal": flatten(note_section),
        "source": {"pdfId": entry_id, "pdfPage": page_number},
        "editorialStatus": "needs-review",
    }


def extract() -> list[dict]:
    reader = PdfReader(PDF)
    records: list[dict] = []

    for page_number, page in enumerate(reader.pages, start=1):
        if page_number <= 4:
            continue
        text = page.extract_text() or ""
        matches = list(ID_LINE.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            records.append(parse_entry(match.group(1), text[match.start() : end], page_number))

    ids = [record["id"] for record in records]
    if len(ids) != 101 or len(set(ids)) != 101 or set(ids) != EXPECTED_IDS:
        missing = sorted(EXPECTED_IDS - set(ids))
        extra = sorted(set(ids) - EXPECTED_IDS)
        raise ValueError(f"Catalogue ID mismatch: count={len(ids)}, missing={missing}, extra={extra}")
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing records")
    args = parser.parse_args()

    records = extract()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    existing = list(OUTPUT.glob("*.json"))
    if existing and not args.force:
        raise SystemExit("Records already exist; refusing to overwrite without --force")

    for record in records:
        path = OUTPUT / f"{record['id']}.json"
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} records to {OUTPUT}")


if __name__ == "__main__":
    main()
