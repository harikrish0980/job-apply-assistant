from typing import Dict
from app.utils import extract_keywords
from app.rewriter import build_highlights


def build_tailored_resume_content(profile: Dict, job: Dict) -> Dict:
    jd_text = job.get("description", "") or ""

    # Ranked, truth-locked highlights (derived from truth bullets vs JD)
    highlights = build_highlights(
        profile.get("truth_bullets", []) or [],
        jd_text,
        max_bullets=10,
    )

    jd_keywords = extract_keywords(jd_text)
    prof_skills = [s.lower() for s in (profile.get("skills", []) or [])]

    return {
        "full_name": profile.get("full_name", ""),
        "email": profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "location": profile.get("location", ""),
        "linkedin": profile.get("linkedin", ""),
        "summary": profile.get("summary", ""),
        "skills": profile.get("skills", []) or [],

        # THIS is the truth-locked tailored content:
        "tailored_highlights": highlights,

        "job_title": job.get("title", ""),
        "company": job.get("company", ""),
        "matched_keywords": [k for k in jd_keywords if k in prof_skills],
        "missing_keywords": [k for k in jd_keywords if k not in prof_skills],
    }
