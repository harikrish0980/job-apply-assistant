import re
from typing import List, Dict, Any

def normalize_text(t: str) -> str:
    t = t or ""
    t = re.sub(r"\s+", " ", t).strip()
    return t

def extract_keywords(text: str) -> List[str]:
    text = (text or "").lower()
    tools = [
        "databricks","spark","python","sql","snowflake","azure","aws","gcp","synapse",
        "adf","airflow","dbt","kafka","hadoop","tableau","power bi","kibana","elasticsearch",
        "terraform","docker","kubernetes","delta lake","pyspark","scala","java","git",
        "fastapi","sqlalchemy","nifi","opensearch","s3","blob storage","lakehouse","druid"
    ]
    found = []
    for k in tools:
        if k in text:
            found.append(k)
    seen = set()
    out = []
    for x in found:
        if x not in seen:
            out.append(x); seen.add(x)
    return out

def safe_slug(s: str, max_len: int = 60) -> str:
    s = (s or "").strip()
    s = re.sub(r"[^a-zA-Z0-9_\- ]+", "", s)
    s = s[:max_len].strip()
    return s.replace(" ", "_")

def render_template(template: str, data: Dict[str, Any]) -> str:
    # Minimal templating: {{KEY}} replacements
    out = template
    for k, v in data.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out
