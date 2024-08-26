import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からデータベース接続情報を取得
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
SSL_CA_PATH = os.getenv("SSL_CA_PATH")

# SSLパスのオプション化
if SSL_CA_PATH:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?ssl_ca={SSL_CA_PATH}"
else:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemyのエンジンを作成
try:
    engine = create_engine(DATABASE_URL)
    logger.info("Database engine created successfully.")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None

# エンジンがNoneの場合の処理
if engine is None:
    raise ValueError("Engine creation failed. Check your DATABASE_URL and database settings.")


# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# デクラレーティブベースの作成
Base = declarative_base()

def get_db():
    db = None
    try:
        db = SessionLocal()
        # データベースに接続できているかを確認
        connection = db.connection()
        logger.info("Database connection established.")
        yield db
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        if db:
            db.close()
    finally:
        if db:
            db.close()
            logger.info("Database connection closed.")