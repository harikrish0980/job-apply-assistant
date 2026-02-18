from typing import List, Tuple
from rapidfuzz import fuzz
from app.utils import extract_keywords, normalize_text

def score_job(profile_skills: List[str], truth_bullets: List[str], jd_text: str) -> Tuple[float, List[str], List[str]]:
    jd = normalize_text(jd_text).lower()
    jd_keywords = extract_keywords(jd)

    prof = [s.lower().strip() for s in (profile_skills or []) if s.strip()]
    prof_set = set(prof)

    matched = [k for k in jd_keywords if k in prof_set]
    missing = [k for k in jd_keywords if k not in prof_set]

    keyword_score = 0.0
    if jd_keywords:
        keyword_score = len(matched) / len(jd_keywords) * 70.0  # up to 70

    bullet_score = 0.0
    if truth_bullets:
        best = 0
        for b in truth_bullets:
            best = max(best, fuzz.token_set_ratio(b.lower(), jd))
        bullet_score = (best / 100.0) * 30.0  # up to 30

    total = round(keyword_score + bullet_score, 2)
    return total, matched, missing
