import pymongo
import os
from dotenv import load_dotenv
from fastapi import HTTPException

# 環境変数をロード
load_dotenv()

# MongoDBの接続情報を取得
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

def get_mongo_collection():
    """
    MongoDBのコレクションを取得する関数
    """
    try:
        # MongoDBクライアントを初期化
        client = pymongo.MongoClient(MONGO_URI)
        
        # データベースを選択
        db = client[MONGO_DB_NAME]
        
        # コレクションを選択
        collection = db[MONGO_COLLECTION_NAME]
        
        return collection
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(e)}")
