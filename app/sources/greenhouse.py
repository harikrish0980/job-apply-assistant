import requests
from typing import List, Dict

def fetch_greenhouse_jobs(company_token: str) -> List[Dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append({
            "source": "greenhouse",
            "company": company_token,
            "title": j.get("title") or "",
            "location": (j.get("location") or {}).get("name"),
            "url": j.get("absolute_url") or "",
            "department": None,
            "description": None,
        })
    return jobs
