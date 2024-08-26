from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# 顧客情報のモデル
class CustomerInformation(Base):
    __tablename__ = 'customer_information'
    
    customer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    email_address = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    projects = relationship("ProjectInformation", back_populates="customer")

# 研究者情報のモデル
class ResearcherInformation(Base):
    __tablename__ = 'researcher_information'
    
    researcher_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    researcher_name = Column(String(255), nullable=False)
    name_kana = Column(String(255), nullable=True)
    university_research_institution = Column(String(255), nullable=True)
    affiliation = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    kaken_url = Column(String(255), nullable=True)
    email_address = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    matching_projects = relationship("MatchingInformation", back_populates="researcher")

# マッチング情報のモデル
class MatchingInformation(Base):
    __tablename__ = 'matching_information'
    
    matching_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('project_information.project_id'))
    researcher_id = Column(Integer, ForeignKey('researcher_information.researcher_id'))
    matching_score = Column(Integer, nullable=True)
    request = Column(Boolean, nullable=True, default=False)
    offer_status = Column(Boolean, nullable=True, default=False)
    response = Column(Boolean, nullable=True, default=False)
    resolution = Column(Boolean, nullable=True, default=False)
    recruitment = Column(Boolean, nullable=True, default=False)
    researcher = relationship("ResearcherInformation", back_populates="matching_projects")
    project = relationship("ProjectInformation", back_populates="matchings")

# プロジェクト情報のモデル
class ProjectInformation(Base):
    __tablename__ = 'project_information'
    
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    consultation_category = Column(String(255), nullable=False)
    project_title = Column(String(255), nullable=False)
    consultation_content = Column(Text, nullable=False)
    research_category = Column(String(255), nullable=True)
    deadline = Column(Date, nullable=True)
    customer_id = Column(Integer, ForeignKey('customer_information.customer_id'))
    project_content_vectorization = Column(Text, nullable=True)
    customer = relationship("CustomerInformation", back_populates="projects")
    matchings = relationship("MatchingInformation", back_populates="project")
