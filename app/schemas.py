from pydantic import BaseModel, Field
from typing import Optional, List

class ProfileIn(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    truth_bullets: List[str] = Field(default_factory=list)

class ProfileOut(BaseModel):
    id: int
    full_name: str
    email: str
    class Config:
        from_attributes = True

class TargetIn(BaseModel):
    company_token: str
    display_name: Optional[str] = None

class JobOut(BaseModel):
    id: int
    source: str
    company: str
    title: str
    location: Optional[str]
    url: str
    class Config:
        from_attributes = True

class PacketOut(BaseModel):
    job_id: int
    packet_path: str
    resume_docx: str
    cover_letter: str
    recruiter_message: str
    match_report: str
