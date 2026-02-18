from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.db import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    skills_csv = Column(Text, nullable=True)      # comma-separated skills
    truth_bullets = Column(Text, nullable=True)   # newline-separated bullets
    resume_text = Column(Text, nullable=True)     # parsed resume text
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)       # greenhouse / lever / linkedin / indeed / dice / company
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    url = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    department = Column(String, nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class Target(Base):
    __tablename__ = "targets"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)       # greenhouse / lever
    company_token = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MatchScore(Base):
    __tablename__ = "match_scores"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, nullable=False, index=True)
    profile_id = Column(Integer, nullable=False, index=True)
    score = Column(Float, nullable=False)
    matched_keywords = Column(Text, nullable=True)    # csv
    missing_keywords = Column(Text, nullable=True)    # csv
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
