# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base, SessionLocal
import models, schemas, crud
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional

import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# SECRET_KEYを環境変数から取得
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# モデルの作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーションの作成
app = FastAPI()

# CORS設定
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベースセッションを取得する依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ユーザー情報を取得するユーティリティ関数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# エンドポイントを追加
@app.get("/")
def read_root():
    return {"message": "Hello World"}


# 顧客情報を新規登録するエンドポイント
@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = crud.create_customer(db, customer)
    if db_customer is None:
        raise HTTPException(status_code=400, detail="Customer already registered")
    return db_customer

# 顧客のログインを処理し、JWTトークンを返すエンドポイント
@app.post("/customers/login", response_model=schemas.Token)
def login_customer(customer: schemas.CustomerLogin, db: Session = Depends(get_db)):
    db_customer = crud.authenticate_customer(db, customer.email_address, customer.password)
    if db_customer is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_customer.email_address}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 研究者情報を新規登録するエンドポイント
@app.post("/researchers/", response_model=schemas.Researcher)
def create_researcher(researcher: schemas.ResearcherCreate, db: Session = Depends(get_db)):
    db_researcher = crud.create_researcher(db, researcher)
    if db_researcher is None:
        raise HTTPException(status_code=400, detail="Researcher already registered")
    return db_researcher

# 研究者のログインを処理し、JWTトークンを返すエンドポイント
@app.post("/researchers/login", response_model=schemas.Token)
def login_researcher(researcher: schemas.ResearcherLogin, db: Session = Depends(get_db)):
    db_researcher = crud.authenticate_researcher(db, researcher.email_address, researcher.password)
    if db_researcher is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_researcher.email_address}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ログインした顧客の情報を取得するエンドポイント
@app.get("/customers/me/", response_model=schemas.Customer)
def read_customers_me(current_customer: schemas.Customer = Depends(get_current_user)):
    return current_customer

# ログインした研究者の情報を取得するエンドポイント
@app.get("/researchers/me/", response_model=schemas.Researcher)
def read_researchers_me(current_researcher: schemas.Researcher = Depends(get_current_user)):
    return current_researcher

# ログインした研究者がオファーがあったプロジェクトの詳細を取得するエンドポイント
@app.get("/researchers/projects", response_model=List[schemas.ProjectInformation])
async def get_researcher_projects(
    db: Session = Depends(get_db),
    current_user: models.ResearcherInformation = Depends(get_current_user)
):
    projects = crud.get_projects_by_researcher(db, current_user.researcher_id)
    return projects

# ログインした研究者が進行中のプロジェクトの詳細を取得するエンドポイント 
@app.get("/researchers/projects/filtered", response_model=List[schemas.ProjectInformation])
async def get_filtered_researcher_projects(
    db: Session = Depends(get_db),
    current_user: models.ResearcherInformation = Depends(get_current_user)
):
    projects = crud.get_filtered_projects_by_researcher(db, current_user.researcher_id)
    return projects

# 研究者がオファーを受け入れるAPI
@app.post("/researchers/accept-offer/{matching_id}", response_model=schemas.MatchingInformation)
async def accept_offer(
    matching_id: int,
    db: Session = Depends(get_db),
    current_user: models.ResearcherInformation = Depends(get_current_user)
):
    matching = crud.accept_offer(db, matching_id)
    if not matching:
        raise HTTPException(status_code=404, detail="Matching not found")
    return matching


# プロジェクト情報を新規登録するエンドポイント
@app.post("/api/projects", response_model=schemas.ProjectInformation)
def create_project(project: schemas.ProjectInformationCreate, db: Session = Depends(get_db), current_user: models.CustomerInformation = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="ログインが必要です")

    db_project = models.ProjectInformation(
        consultation_category=project.consultation_category,
        project_title=project.project_title,
        consultation_content=project.consultation_content,
        research_category=project.research_category,
        deadline=project.deadline,
        customer_id=current_user.customer_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)  # この時点で project_id が自動的に設定されます
    return db_project

# 特定のプロジェクト情報を取得するエンドポイント
@app.get("/api/projects/{project_id}", response_model=schemas.ProjectInformation)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.ProjectInformation).filter(models.ProjectInformation.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# # 新規: 研究者を提案するエンドポイント
# @app.post("/api/projects/{project_id}/match-researchers", response_model=List[schemas.MatchingResult])
# async def match_researchers(
#     project_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.CustomerInformation = Depends(get_current_user)
# ):
#     # プロジェクトを取得
#     project = db.query(models.ProjectInformation).filter(models.ProjectInformation.project_id == project_id).first()
#     if not project:
#         raise HTTPException(status_code=404, detail="Project not found")
    
#     # マッチングアルゴリズムを実行
#     from .matching import run_matching_algorithm
#     matching_results_raw = run_matching_algorithm(project.consultation_content)

#     # 結果をスキーマに合わせて整形
#     matching_results = []
#     for result in matching_results_raw:
#         matching_result = {
#             "project_title": project.project_title,  # プロジェクトのタイトルを追加
#             "matching_score": result['score'],  # スコアをマッチングスコアとして使用
#             "researcher_name": result['researcher_name'],
#             "name_kana": result.get('name_kana'),
#             "university_research_institution": result.get('university_research_institution'),
#             "affiliation": result.get('affiliation'),
#             "position": result.get('position'),
#             "kaken_url": result.get('kaken_url'),
#         }
#         matching_results.append(matching_result)

#         # DB にマッチング結果を保存
#         db_matching = models.MatchingInformation(
#             project_id=project_id,
#             researcher_id=result['researcher_id'],
#             matching_score=result['score'],
#             request=False,
#             offer_status=False,
#             response=False,
#             resolution=False,
#             recruitment=False
#         )
#         db.add(db_matching)

#     db.commit()
#     return matching_results

@app.post("/api/projects/{project_id}/match-researchers", response_model=List[schemas.MatchingResult])
async def match_researchers(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.CustomerInformation = Depends(get_current_user)
):
    # プロジェクトを取得
    project = db.query(models.ProjectInformation).filter(models.ProjectInformation.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # マッチングアルゴリズムを実行
    from .matching import run_matching_algorithm
    matching_results_raw = run_matching_algorithm(project.consultation_content)

    # 結果をスキーマに合わせて整形
    matching_results = []
    for result in matching_results_raw:
        matching_result = {
            "project_title": project.project_title,  # プロジェクトのタイトルを追加
            "matching_score": result['score'],  # スコアをマッチングスコアとして使用
            "researcher_name": result.get('researcher_name', 'Unknown'),
            "name_kana": result.get('name_kana', ''),
            "university_research_institution": result.get('university_research_institution', ''),
            "affiliation": result.get('affiliation', ''),
            "position": result.get('position', ''),
            "kaken_url": result.get('kaken_url', ''),
        }
        matching_results.append(matching_result)

        # DB にマッチング結果を保存
        db_matching = models.MatchingInformation(
            project_id=project_id,
            researcher_id=result['researcher_id'],
            matching_score=result['score'],
            request=False,
            offer_status=False,
            response=False,
            resolution=False,
            recruitment=False
        )
        db.add(db_matching)

    db.commit()
    return matching_results


# プロジェクトIDに紐づくマッチング結果を取得するエンドポイント
# @app.get("/api/projects/{project_id}/matching", response_model=List[schemas.MatchingResult])
# async def get_matching_results(
#     project_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.CustomerInformation = Depends(get_current_user)
# ):
#     # プロジェクトに紐づくマッチング結果を取得
#     matching_results = db.query(models.MatchingInformation).filter(models.MatchingInformation.project_id == project_id).all()
#     if not matching_results:
#         raise HTTPException(status_code=404, detail="Matching results not found")
#     return matching_results

@app.get("/api/projects/{project_id}/matching", response_model=List[schemas.MatchingResult])
async def get_matching_results(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.CustomerInformation = Depends(get_current_user)
):
    # Join MatchingInformation with ResearcherInformation and ProjectInformation
    matching_results = db.query(
        models.MatchingInformation.matching_score,
        models.ProjectInformation.project_title,
        models.ResearcherInformation.researcher_name,
        models.ResearcherInformation.name_kana,
        models.ResearcherInformation.university_research_institution,
        models.ResearcherInformation.affiliation,
        models.ResearcherInformation.position,
        models.ResearcherInformation.kaken_url,
    ).join(
        models.ProjectInformation, models.MatchingInformation.project_id == models.ProjectInformation.project_id
    ).join(
        models.ResearcherInformation, models.MatchingInformation.researcher_id == models.ResearcherInformation.researcher_id
    ).filter(
        models.MatchingInformation.project_id == project_id
    ).all()

    if not matching_results:
        raise HTTPException(status_code=404, detail="Matching results not found")
    
    return matching_results




