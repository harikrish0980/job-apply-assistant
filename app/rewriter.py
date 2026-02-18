from typing import List, Dict, Tuple
from rapidfuzz import fuzz
from app.utils import normalize_text, extract_keywords

def rank_truth_bullets(truth_bullets: List[str], jd_text: str) -> List[Tuple[int, str, float]]:
    """
    Returns bullets ranked by relevance to JD.
    Score uses:
      - keyword hits from extract_keywords
      - fuzzy match to JD
    """
    jd = normalize_text(jd_text).lower()
    jd_kws = extract_keywords(jd)

    ranked = []
    for i, b in enumerate(truth_bullets or []):
        b_norm = normalize_text(b)
        b_low = b_norm.lower()

        kw_hits = sum(1 for k in jd_kws if k in b_low)
        fuzzy = fuzz.token_set_ratio(b_low, jd) / 100.0  # 0..1

        # Weighted score: keyword hits matter + fuzzy tie-breaker
        score = (kw_hits * 2.0) + (fuzzy * 3.0)
        ranked.append((i, b_norm, score))

    ranked.sort(key=lambda x: x[2], reverse=True)
    return ranked

def build_highlights(truth_bullets: List[str], jd_text: str, max_bullets: int = 10) -> List[str]:
    ranked = rank_truth_bullets(truth_bullets, jd_text)
    selected = [b for _, b, _ in ranked[:max_bullets]]

    # fallback if JD empty or nothing matches
    if not selected and truth_bullets:
        selected = [normalize_text(b) for b in truth_bullets[:max_bullets]]
    return selected

def reorder_experience_sections(experiences: List[Dict], jd_text: str) -> List[Dict]:
    """
    experiences = list of dicts like:
      { "company": "...", "role": "...", "bullets": [...] }

    We rank each experience by how relevant its bullets are to JD,
    then reorder experiences descending (most relevant first).
    """
    jd = normalize_text(jd_text).lower()
    scored = []

    for exp in experiences:
        bullets = exp.get("bullets", []) or []
        best = 0
        for b in bullets:
            best = max(best, fuzz.token_set_ratio((b or "").lower(), jd))
        scored.append((best, exp))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored]
