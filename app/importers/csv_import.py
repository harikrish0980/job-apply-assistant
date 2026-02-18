import csv
from io import StringIO
from typing import List, Dict

REQUIRED = ["source","company","title","url"]

def parse_jobs_csv(csv_text: str) -> List[Dict]:
    f = StringIO(csv_text)
    reader = csv.DictReader(f)
    rows = []
    for row in reader:
        r = {k.strip(): (v or "").strip() for k, v in row.items()}
        for req in REQUIRED:
            if not r.get(req):
                raise ValueError(f"Missing required column '{req}' in a row.")
        rows.append({
            "source": r.get("source","import"),
            "company": r.get("company",""),
            "title": r.get("title",""),
            "location": r.get("location") or None,
            "url": r.get("url",""),
            "description": r.get("description") or "",
            "department": r.get("department") or None,
        })
    return rows
