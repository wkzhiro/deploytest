from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# 顧客情報のスキーマ
class CustomerCreate(BaseModel):
    customer_name: str
    company_name: str
    department: str
    email_address: str
    password: str

class Customer(BaseModel):
    customer_id: int
    customer_name: str
    company_name: str
    department: str
    email_address: str

    class Config:
        from_attributes = True

class CustomerLogin(BaseModel):
    email_address: str
    password: str
    
# 研究者情報のスキーマ
class ResearcherCreate(BaseModel):
    researcher_name: str
    university_research_institution: str
    affiliation: str
    position: str
    kaken_url: Optional[str] = None
    email_address: str
    password: str

class Researcher(BaseModel):
    researcher_id: int
    researcher_name: str
    university_research_institution: str
    affiliation: str
    position: str
    kaken_url: Optional[str] = None
    email_address: str

    class Config:
        from_attributes = True

class ResearcherLogin(BaseModel):
    email_address: str
    password: str

# Matching Info
class MatchingInformation(BaseModel):
    matching_id: int
    project_id: int
    researcher_id: int
    matching_score: Optional[int] = None
    request: Optional[bool] = None
    offer_status: Optional[bool] = None
    response: Optional[bool] = None
    resolution: Optional[bool] = None
    recruitment: Optional[bool] = None

    class Config:
        from_attributes = True
        
# Project Info
class ProjectInformation(BaseModel):
    project_id: int
    consultation_category: Optional[str] = None
    project_title: Optional[str] = None
    consultation_content: Optional[str] = None
    research_category: Optional[str] = None
    deadline: Optional[date] = None
    customer_id: Optional[int] = None
    matching_id: Optional[int] = None
    project_content_vectorization: Optional[str] = None
    customer: Optional[Customer] = None #顧客情報追加　byこばくみ 8/21

    class Config:
        from_attributes = True
        
# 新規作成スキーマの追加
class ProjectInformationCreate(BaseModel):
    consultation_category: str
    project_title: str
    consultation_content: str
    research_category: str
    deadline: Optional[date] = None

    class Config:
        from_attributes = True

# トークンの追加
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    
# Matching Result スキーマ
class MatchingResult(BaseModel):
    project_title: Optional[str] = None
    matching_score: Optional[int] = None
    researcher_name: Optional[str] = None
    name_kana: Optional[str] = None
    university_research_institution: Optional[str] = None
    affiliation: Optional[str] = None
    position: Optional[str] = None
    kaken_url: Optional[str] = None

    class Config:
        from_attributes = True
