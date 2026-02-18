import os
import json
import io
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.config import settings
from app import models, schemas
from app.sources.greenhouse import fetch_greenhouse_jobs
from app.sources.lever import fetch_lever_jobs
from app.scoring import score_job
from app.tailoring import build_tailored_resume_content
from app.docgen import generate_resume_docx
from app.utils import safe_slug, render_template
from app.importers.csv_import import parse_jobs_csv

from pypdf import PdfReader

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name)


def _profile_to_dict(p: models.Profile) -> dict:
    skills = [s.strip() for s in (p.skills_csv or "").split(",") if s.strip()]
    bullets = [b.strip() for b in (p.truth_bullets or "").split("\n") if b.strip()]
    return {
        "id": p.id,
        "full_name": p.full_name,
        "email": p.email,
        "phone": p.phone,
        "location": p.location,
        "linkedin": p.linkedin,
        "summary": p.summary,
        "skills": skills,
        "truth_bullets": bullets,
        "resume_text": p.resume_text or "",
    }


# Change 1: replace POST /profile logic to “update if exists”
@app.post("/profile", response_model=schemas.ProfileOut)
def create_or_update_profile(payload: schemas.ProfileIn, db: Session = Depends(get_db)):
    existing = db.query(models.Profile).first()

    if existing:
        existing.full_name = payload.full_name
        existing.email = payload.email
        existing.phone = payload.phone
        existing.location = payload.location
        existing.linkedin = payload.linkedin
        existing.summary = payload.summary
        existing.skills_csv = ",".join(payload.skills)
        existing.truth_bullets = "\n".join(payload.truth_bullets)
        db.commit()
        db.refresh(existing)
        return existing

    p = models.Profile(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        location=payload.location,
        linkedin=payload.linkedin,
        summary=payload.summary,
        skills_csv=",".join(payload.skills),
        truth_bullets="\n".join(payload.truth_bullets),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# Change 2: add GET /profile to confirm what’s saved
@app.get("/profile", response_model=schemas.ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    p = db.query(models.Profile).first()
    if not p:
        raise HTTPException(status_code=404, detail="No profile found")
    return p


@app.post("/profile/resume/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile:
        raise HTTPException(400, "Create a profile first with POST /profile")

    filename = (file.filename or "").lower()
    content = await file.read()

    text = ""
    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content))  # type: ignore
        except Exception:
            # fallback: write temp
            tmp = "./data/_tmp_resume.pdf"
            os.makedirs("./data", exist_ok=True)
            with open(tmp, "wb") as f:
                f.write(content)
            reader = PdfReader(tmp)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    else:
        raise HTTPException(
            400,
            "Only PDF resume parsing is enabled in this starter. (DOCX parsing can be added later.)",
        )

    profile.resume_text = text.strip()
    db.commit()
    return {"ok": True, "chars": len(profile.resume_text)}


@app.post("/targets/greenhouse")
def add_greenhouse_target(payload: schemas.TargetIn, db: Session = Depends(get_db)):
    t = models.Target(
        source="greenhouse",
        company_token=payload.company_token,
        display_name=payload.display_name,
    )
    db.add(t)
    db.commit()
    return {"ok": True}


@app.post("/targets/lever")
def add_lever_target(payload: schemas.TargetIn, db: Session = Depends(get_db)):
    t = models.Target(
        source="lever",
        company_token=payload.company_token,
        display_name=payload.display_name,
    )
    db.add(t)
    db.commit()
    return {"ok": True}


@app.post("/jobs/refresh")
def refresh_jobs(db: Session = Depends(get_db)):
    targets = db.query(models.Target).all()
    if not targets:
        raise HTTPException(400, "No targets found. Add greenhouse/lever targets first.")

    inserted = 0
    for t in targets:
        if t.source == "greenhouse":
            jobs = fetch_greenhouse_jobs(t.company_token)
        elif t.source == "lever":
            jobs = fetch_lever_jobs(t.company_token)
        else:
            continue

        for j in jobs:
            if not j.get("url"):
                continue
            exists = db.query(models.Job).filter(models.Job.url == j["url"]).first()
            if exists:
                continue
            db.add(models.Job(**j))
            inserted += 1
    db.commit()
    return {"inserted": inserted}


@app.post("/jobs/import/csv")
async def import_jobs_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8", errors="replace")
    rows = parse_jobs_csv(content)
    inserted = 0
    for j in rows:
        exists = db.query(models.Job).filter(models.Job.url == j["url"]).first()
        if exists:
            continue
        db.add(models.Job(**j))
        inserted += 1
    db.commit()
    return {"inserted": inserted}


@app.get("/jobs/top", response_model=list[schemas.JobOut])
def top_jobs(limit: int = 25, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile:
        raise HTTPException(400, "Create a profile first with POST /profile")
    prof = _profile_to_dict(profile)

    jobs = db.query(models.Job).filter(models.Job.is_active == True).all()
    scored = []
    for job in jobs:
        s, matched, missing = score_job(
            prof["skills"], prof["truth_bullets"], job.description or ""
        )
        scored.append((s, job))
        ms = (
            db.query(models.MatchScore)
            .filter(
                models.MatchScore.job_id == job.id,
                models.MatchScore.profile_id == profile.id,
            )
            .first()
        )
        if not ms:
            ms = models.MatchScore(
                job_id=job.id,
                profile_id=profile.id,
                score=s,
                matched_keywords=",".join(matched),
                missing_keywords=",".join(missing),
            )
            db.add(ms)
        else:
            ms.score = s
            ms.matched_keywords = ",".join(matched)
            ms.missing_keywords = ",".join(missing)
    db.commit()

    scored.sort(key=lambda x: x[0], reverse=True)
    return [j for _, j in scored[:limit]]


@app.post("/packets/generate/{job_id}", response_model=schemas.PacketOut)
def generate_packet(job_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile:
        raise HTTPException(400, "Create a profile first with POST /profile")
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    prof = _profile_to_dict(profile)
    job_dict = {
        "id": job.id,
        "source": job.source,
        "company": job.company,
        "title": job.title,
        "location": job.location,
        "url": job.url,
        "description": job.description or "",
    }

    content = build_tailored_resume_content(prof, job_dict)

    safe_company = safe_slug(job.company, 40)
    safe_title = safe_slug(job.title, 60)
    packet_dir = os.path.join(
        settings.packets_dir, f"{safe_company}_{safe_title}_{job.id}"
    )
    os.makedirs(packet_dir, exist_ok=True)

    base_resume = os.path.join(settings.templates_dir, "resume_base.docx")
    if not os.path.exists(base_resume):
        raise HTTPException(
            400, f"Missing template: {base_resume}. Put your resume template there."
        )

    resume_docx = os.path.join(packet_dir, "resume_tailored.docx")
    generate_resume_docx(base_resume, resume_docx, content)

    # cover letter templating
    cover_template_path = os.path.join(settings.templates_dir, "cover_letter.md")
    cover_template = ""
    if os.path.exists(cover_template_path):
        with open(cover_template_path, "r", encoding="utf-8") as f:
            cover_template = f.read()
    else:
        cover_template = (
            "Hi {{HIRING_TEAM}},\n\nI’m applying for {{JOB_TITLE}} at {{COMPANY}}.\n\n"
            "Thanks,\n{{FULL_NAME}}"
        )

    matched_bullets = ""
    mk = content.get("matched_keywords") or []
    if mk:
        matched_bullets = "\n".join([f"- {k}" for k in mk[:10]])
    else:
        matched_bullets = "- data engineering\n- analytics\n- production pipelines"

    cover_data = {
        "HIRING_TEAM": "Hiring Team",
        "JOB_TITLE": job.title,
        "COMPANY": job.company,
        "FULL_NAME": prof["full_name"],
        "MATCHED_BULLETS": matched_bullets,
    }
    cover = render_template(cover_template, cover_data)

    cover_letter_path = os.path.join(packet_dir, "cover_letter.md")
    recruiter_msg_path = os.path.join(packet_dir, "recruiter_message.txt")
    report_path = os.path.join(packet_dir, "match_report.json")

    with open(cover_letter_path, "w", encoding="utf-8") as f:
        f.write(cover)

    recruiter_msg = f"""Hi — I’m interested in the {job.title} role at {job.company}.
I have hands-on experience in {", ".join((content.get("matched_keywords") or [])[:6]) or "data engineering"} and can share a tailored resume.
Are you the right person to speak with about next steps?
"""
    with open(recruiter_msg_path, "w", encoding="utf-8") as f:
        f.write(recruiter_msg)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "job": job_dict,
                "profile_id": prof["id"],
                "matched_keywords": content.get("matched_keywords"),
                "missing_keywords": content.get("missing_keywords"),
                "tailored_bullets_used": content.get("tailored_bullets"),
                "apply_url": job.url,
                "note": "This tool generates documents and tracking data. Submit applications manually on the job site.",
            },
            f,
            indent=2,
        )

    return schemas.PacketOut(
        job_id=job.id,
        packet_path=packet_dir,
        resume_docx=resume_docx,
        cover_letter=cover_letter_path,
        recruiter_message=recruiter_msg_path,
        match_report=report_path,
    )
