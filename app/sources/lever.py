import requests
from typing import List, Dict

def fetch_lever_jobs(company_token: str) -> List[Dict]:
    url = f"https://api.lever.co/v0/postings/{company_token}?mode=json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    arr = r.json()
    jobs = []
    for j in arr:
        jobs.append({
            "source": "lever",
            "company": company_token,
            "title": j.get("text") or "",
            "location": (j.get("categories") or {}).get("location"),
            "url": j.get("hostedUrl") or "",
            "department": (j.get("categories") or {}).get("team"),
            "description": j.get("descriptionPlain") or j.get("description") or "",
        })
    return jobs
