import os
import csv
from datetime import datetime
from typing import Dict

TRACKER_HEADERS = [
    "timestamp",
    "job_id",
    "source",
    "company",
    "title",
    "location",
    "url",
    "score",
    "packet_path",
    "resume_docx",
    "cover_letter",
    "recruiter_message",
    "match_report",
    "status"
]

def append_tracker_row(csv_path: str, row: Dict) -> None:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
