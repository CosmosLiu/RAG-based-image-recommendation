from fastapi import FastAPI, HTTPException
import uvicorn
from schemas import SaveImageRequest, TextRecommendRequest, ImageRecommendRequest, RecommendResponse
from milvus_db import MilvusModel
from feature_service import extract_features_from_image, extract_features_from_text

app = FastAPI(title="Image RAG Demo")

print("初始化 Milvus 客户端实例...")
milvus_db = MilvusModel(auto_create=True, load_collection=True)
print("Milvus 实例就绪！")

@app.post("/api/v1/images/rag")
async def save_image_rag(request: SaveImageRequest):
    """保存图片 RAG 数据"""
    print(f"\n{'='*60}\n[API 接口请求] -> 保存图片入库 (RAG)")
    print(f"用户 UID: {request.uid}")
    print(f"图片 URL: {request.image_url}")
    
    if milvus_db.check_exists(request.uid, request.image_url):
        print("=> 提示: 当前图片 URL 数据已存在于向量库中，跳过处理。")
        print(f"{'='*60}\n")
        return {"message": "Image already exists."}
    
    # 步骤1 & 2：提取文本特征并转换为向量
    features = extract_features_from_image(request.image_url)
    
    print("\n▶ 步骤 3: 正在将多路向量和元数据存入 Milvus 数据库...")
    data = {
        "uid": request.uid,
        "image_id": request.image_url, 
        "visible_context": features["visible_context"],
        "visible_context_vector": features["visible_context_vector"],
        "hidden_context": features["hidden_context"],
        "hidden_context_vector": features["hidden_context_vector"],
        "description": features["description"],
        "description_vector": features["description_vector"]
    }
    milvus_db.insert_data([data])
    print("=> 成功! 图片 RAG 多路数据已安全落盘到 Milvus。")
    print(f"{'='*60}\n")
    return {"message": "Success", "image_url": request.image_url}


@app.post("/api/v1/recommend/text", response_model=RecommendResponse)
async def recommend_by_text(request: TextRecommendRequest):
    """接收字符串，获取推荐图片的 url"""
    print(f"\n{'='*60}\n[API 接口请求] -> 文本搜图片 (推荐)")
    print(f"用户 UID: {request.uid}")
    print(f"搜索查询: {request.query}")
    print(f"请求返回数量: {request.top_k} 张")
    
    try:
        # 步骤1 & 2: 提取查询词的三路查询向量
        query_docs = extract_features_from_text(request.query)
        
        print("\n▶ 步骤 3: 正在 Milvus 向量库中进行混合检索(Hybrid Search)...")
        search_results = milvus_db.search(request.uid, query_docs, request.top_k)
        
        image_urls = [res.get("image_id") for res in search_results if "image_id" in res]
        
        print(f"=> 检索完成! 基于【显性权重0.4, 隐性0.2, 描述0.4】，最终召回 {len(image_urls)} 张匹配图片:")
        for idx, url in enumerate(image_urls, 1):
            print(f"   [{idx}] {url}")
        print(f"{'='*60}\n")
            
        return RecommendResponse(results=image_urls)
    except Exception as e:
        print(f"执行出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recommend/image", response_model=RecommendResponse)
async def recommend_by_image(request: ImageRecommendRequest):
    """接收图片 url，获取推荐图片的 url"""
    print(f"\n{'='*60}\n[API 接口请求] -> 图片搜图片 (推荐)")
    print(f"用户 UID: {request.uid}")
    print(f"参考图片 URL: {request.image_url}")
    print(f"请求返回数量: {request.top_k} 张")
    
    try:
        # 步骤1 & 2: 提取当前参考图片的特征与向量
        features = extract_features_from_image(request.image_url)
        
        query_docs = {
            "visible": {"vector": features["visible_context_vector"]},
            "hidden": {"vector": features["hidden_context_vector"]},
            "description": {"vector": features["description_vector"]}
        }
        
        print("\n▶ 步骤 3: 正在基于相似度在 Milvus 向量库中进行多路检索...")
        search_results = milvus_db.search(request.uid, query_docs, request.top_k)
        image_urls = [res.get("image_id") for res in search_results if "image_id" in res]
        
        # 过滤掉当前传入的参考图片本身
        image_urls = [url for url in image_urls if url != request.image_url]
        
        print(f"=> 检索完成! 找到 {len(image_urls)} 张高度相似的推荐图片:")
        for idx, url in enumerate(image_urls, 1):
            print(f"   [{idx}] {url}")
        print(f"{'='*60}\n")
            
        return RecommendResponse(results=image_urls)
    except Exception as e:
        print(f"执行出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 配置了简单的启动服务器日志
    print("正在启动 FastAPI 服务 (http://0.0.0.0:8000)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
