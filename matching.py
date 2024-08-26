from sentence_transformers import SentenceTransformer
from database_mongo import get_mongo_collection

def get_embedding(text):
    """
    相談内容をベクトル化するための関数
    """
    model = SentenceTransformer('nomic-ai/nomic-embed-text-v1', trust_remote_code=True)
    embedding = model.encode(text)
    return embedding.tolist()

def run_matching_algorithm(consultation_content):
    """
    プロジェクトの相談内容に基づいて最適な研究者を提案するためのアルゴリズム
    """
    # MongoDBからコレクションを取得
    collection = get_mongo_collection()

    # 相談内容をベクトル化
    query_embedding = get_embedding(consultation_content)

    # サンプルベクター検索パイプラインを定義
    pipeline = [
       {
          "$vectorSearch": {
                "index": "vector_index3",
                "queryVector": query_embedding,
                "path": "research_content_embedding",
                "numCandidates": 1000,
                "limit": 100
          }
       },
       {
          "$project": {
             "_id": 0,
             "researcher_id": 1,
             "researcher_name": 1,
             "name_kana": 1,
             "university_research_institution": 1,
             "affiliation": 1,
             "position": 1,
             "kaken_url": 1,
             "research_content": 1,
             "score": {
                "$meta": "vectorSearchScore"
             }
          }
       },
       {
          "$sort": {
             "score": -1
          }
       },
       {
          "$limit": 100
       }
    ]

    # MongoDBに対して検索を実行
    results_cursor = collection.aggregate(pipeline)
    results_list = list(results_cursor)

    # 重複のない結果をリストに変換し、スコアでソート
    unique_results_dict = {}
    for result in results_list:
        key = (result['researcher_id'], result['researcher_name'])
        if key not in unique_results_dict or result['score'] > unique_results_dict[key]['score']:
            # スコアを100倍して整数に変換
            result['score'] = int(result['score'] * 100)
            unique_results_dict[key] = result

    sorted_results = sorted(unique_results_dict.values(), key=lambda x: x['score'], reverse=True)

    # 上位10件を返す
    return sorted_results[:10]
