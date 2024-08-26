from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 顧客情報を作成する関数
def create_customer(db: Session, customer: schemas.CustomerCreate):
    hashed_password = pwd_context.hash(customer.password)
    db_customer = models.CustomerInformation(
        customer_name=customer.customer_name,
        company_name=customer.company_name,
        department=customer.department,
        email_address=customer.email_address,
        password=hashed_password
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# 顧客のログイン情報を検証する関数
def authenticate_customer(db: Session, email_address: str, password: str):
    db_customer = db.query(models.CustomerInformation).filter(models.CustomerInformation.email_address == email_address).first()
    if not db_customer:
        return None
    if not pwd_context.verify(password, db_customer.password):
        return None
    return db_customer

# 研究者情報を作成する関数
def create_researcher(db: Session, researcher: schemas.ResearcherCreate):
    hashed_password = pwd_context.hash(researcher.password)
    db_researcher = models.ResearcherInformation(
        researcher_name=researcher.researcher_name,
        name_kana=researcher.name_kana,
        university_research_institution=researcher.university_research_institution,
        affiliation=researcher.affiliation,
        position=researcher.position,
        kaken_url=researcher.kaken_url,
        email_address=researcher.email_address,
        password=hashed_password
    )
    db.add(db_researcher)
    db.commit()
    db.refresh(db_researcher)
    return db_researcher

# 研究者のログイン情報を検証する関数
def authenticate_researcher(db: Session, email_address: str, password: str):
    db_researcher = db.query(models.ResearcherInformation).filter(models.ResearcherInformation.email_address == email_address).first()
    if not db_researcher:
        return None
    if not pwd_context.verify(password, db_researcher.password):
        return None
    return db_researcher

# 顧客および研究者の両方からユーザー情報を取得する関数
def get_user_by_email(db: Session, email: str):
    user = db.query(models.CustomerInformation).filter(models.CustomerInformation.email_address == email).first()
    if not user:
        user = db.query(models.ResearcherInformation).filter(models.ResearcherInformation.email_address == email).first()
    return user

# 研究者でプロジェクトをソート　オファーの合った案件(update by こばくみ8/21)
def get_projects_by_researcher(db: Session, researcher_id: int):
    # ProjectInformationとMatchingInformationを結合し、matching_idも取得するように修正
    projects = db.query(models.ProjectInformation, models.MatchingInformation.matching_id).join(models.MatchingInformation).filter(
        models.MatchingInformation.researcher_id == researcher_id,
        models.MatchingInformation.project_id == models.ProjectInformation.project_id,
        models.MatchingInformation.request == True,
        models.MatchingInformation.response == False
    ).all()
    
    project_details = []
    # 取得したタプルからprojectとmatching_idを取得する
    for project, matching_id in projects:
        customer = db.query(models.CustomerInformation).filter(models.CustomerInformation.customer_id == project.customer_id).first()
        project_detail = {
            "project_id": project.project_id,
            "matching_id": matching_id,  # タプルから取得したmatching_idを使用
            "consultation_category": project.consultation_category,
            "project_title": project.project_title,
            "consultation_content": project.consultation_content,
            "research_category": project.research_category,
            "deadline": project.deadline.isoformat() if project.deadline else None,
            "customer": {
                "customer_id": customer.customer_id,
                "customer_name": customer.customer_name,
                "company_name": customer.company_name,
                "department": customer.department,
                "email_address": customer.email_address
            }
        }
        project_details.append(project_detail)
    
    return project_details

# 研究者でプロジェクトをソート　進行中案件(update by こばくみ8/21)
def get_filtered_projects_by_researcher(db: Session, researcher_id: int):
  # ProjectInformationとMatchingInformationを結合し、matching_idも取得するように修正
    projects = db.query(models.ProjectInformation, models.MatchingInformation.matching_id).join(models.MatchingInformation).filter(
        models.MatchingInformation.researcher_id == researcher_id,
        models.MatchingInformation.project_id == models.ProjectInformation.project_id,
        models.MatchingInformation.request == True,
        models.MatchingInformation.response == True
    ).all()
    
    project_details = []
    # 取得したタプルからprojectとmatching_idを取得する
    for project, matching_id in projects:
        customer = db.query(models.CustomerInformation).filter(models.CustomerInformation.customer_id == project.customer_id).first()
        project_detail = {
            "project_id": project.project_id,
            "matching_id": matching_id,  # タプルから取得したmatching_idを使用
            "consultation_category": project.consultation_category,
            "project_title": project.project_title,
            "consultation_content": project.consultation_content,
            "research_category": project.research_category,
            "deadline": project.deadline.isoformat() if project.deadline else None,
            "customer": {
                "customer_id": customer.customer_id,
                "customer_name": customer.customer_name,
                "company_name": customer.company_name,
                "department": customer.department,
                "email_address": customer.email_address
            }
        }
        project_details.append(project_detail)
    
    return project_details
 

# マッチング情報のresponseを更新する関数
def accept_offer(db: Session, matching_id: int):
    matching = db.query(models.MatchingInformation).filter(models.MatchingInformation.matching_id == matching_id).first()
    if not matching:
        return None
    matching.response = True
    db.commit()
    db.refresh(matching)
    return matching

# プロジェクト詳細を表示
def get_project_details(db: Session, project_id: int):
    return db.query(models.ProjectInformation).filter(models.ProjectInformation.project_id == project_id).first()