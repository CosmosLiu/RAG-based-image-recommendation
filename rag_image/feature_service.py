import requests
import base64
import json
import time
from typing import Dict, Any

# ================= 配置区 =================
# Ollama 默认提供的 OpenAI 兼容接口地址
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama" # Ollama 不需要真的 key，随便填即可

# 模型名称配置 (需与 ollama list 中的名称一致)
VISION_MODEL = "qwen3-vl:8b"     # 用于处理图片和视觉
TEXT_MODEL = "qwen3-vl:8b"       # 用于扩写文本查询 (复用大模型)
EMBEDDING_MODEL = "bge-m3"       # 向量模型 (注意：bge-m3 是 1024 维)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
# ==========================================

def get_embedding(text: str, name: str = "") -> list[float]:
    """调用 Ollama Embedding 接口获取文本向量"""
    print(f"      [Embedding] 正在生成【{name}】的向量 (使用模型: {EMBEDDING_MODEL})...")
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
    }
    t0 = time.time()
    response = requests.post(f"{BASE_URL}/embeddings", headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"Embedding API Error: {response.text}")
    print(f"      [Embedding] 向量生成完毕，耗时 {time.time()-t0:.2f} 秒")
    return response.json()['data'][0]['embedding']


def call_chat_completion(messages: list, model: str) -> Dict[str, str]:
    """调用 Ollama 对话接口，要求返回 JSON 字符串并解析"""
    payload = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"} 
    }
    t0 = time.time()
    response = requests.post(f"{BASE_URL}/chat/completions", headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"LLM API Error: {response.text}")
    
    print(f"    [大模型] 思考与推理调用成功，耗时 {time.time()-t0:.2f} 秒")
    content = response.json()['choices'][0]['message']['content']
    try:
        content = content.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except json.JSONDecodeError:
        print(f"    [警告] 大模型返回的不是合法 JSON: {content}")
        return {
            "visible_context": "未知",
            "hidden_context": "未知",
            "description": content
        }


def get_image_base64(image_url: str) -> str:
    """下载图片并转为 Base64（支持 HTTP URL 和本地文件路径）"""
    if image_url.startswith("http"):
        print(f"  [图片下载] 正在从外部 URL 抓取图片到内存中: {image_url}")
        t0 = time.time()
        resp = requests.get(image_url)
        resp.raise_for_status()
        mime_type = resp.headers.get("Content-Type", "image/jpeg")
        base64_data = base64.b64encode(resp.content).decode("utf-8")
        print(f"  [图片下载] 抓取成功！图片大小: {len(resp.content)/1024:.2f} KB，耗时 {time.time()-t0:.2f} 秒")
        return f"data:{mime_type};base64,{base64_data}"
    else:
        print(f"  [图片读取] 正在从本地路径读取图片: {image_url}")
        import os
        if not os.path.exists(image_url):
            raise ValueError(f"本地文件不存在: {image_url}")
        ext = os.path.splitext(image_url)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp"}
        mime_type = mime_map.get(ext, "image/jpeg")
        with open(image_url, "rb") as f:
            content = f.read()
        base64_data = base64.b64encode(content).decode("utf-8")
        print(f"  [图片读取] 读取成功！图片大小: {len(content)/1024:.2f} KB")
        return f"data:{mime_type};base64,{base64_data}"


def extract_features_from_image(image_url: str) -> Dict[str, Any]:
    print(f"\n▶ 步骤 1/2: 开始提取图片特征...")
    
    # 提前获取图片的 Base64
    img_b64 = get_image_base64(image_url)
    
    prompt = """
    请仔细观察这张图片，并以 JSON 对象的形式返回以下三个维度的信息：
    1. "visible_context": 图片的显性特征（包括具体的物体、人物、颜色、形状、文字等客观存在的元素，不超过100字）。
    2. "hidden_context": 图片的隐性特征（传达的氛围、情感、艺术风格、深层含义或背景故事等，不超过100字）。
    3. "description": 对整张图片的详细综合描述（不超过500字）。
    注意：只返回合法的 JSON 格式，不要包含其他任何解释。
    """
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": img_b64}}
            ]
        }
    ]
    
    print(f"  [视觉模型] 正在呼叫 {VISION_MODEL} 深入分析图片细节...")
    text_features = call_chat_completion(messages, VISION_MODEL)
    visible_text = text_features.get("visible_context", "无")
    hidden_text = text_features.get("hidden_context", "无")
    description_text = text_features.get("description", "无")

    print(f"  [特征结果] 多路语义特征提取完成：")
    print(f"    - 显性特征: {visible_text}")
    print(f"    - 隐性特征: {hidden_text}")
    print(f"    - 整体描述: {description_text}")

    print(f"\n▶ 步骤 2/2: 正在将多路特征文本转换为高维向量(1024维)...")
    return {
        "visible_context": visible_text,
        "visible_context_vector": get_embedding(visible_text, "显性特征"),
        "hidden_context": hidden_text,
        "hidden_context_vector": get_embedding(hidden_text, "隐性特征"),
        "description": description_text,
        "description_vector": get_embedding(description_text, "整体描述")
    }


def extract_features_from_text(query: str) -> Dict[str, Any]:
    print(f"\n▶ 步骤 1/2: 正在将简短搜索词「{query}」扩写为多路特征...")
    
    prompt = f"""
    用户输入了一个搜索图片的查询词："{query}"。
    为了在向量数据库中进行高精度的多路召回，请你发挥想象力，将这个查询词扩写并拆解为三个维度的描述，以便能匹配到对应的图片。
    请以 JSON 对象的形式返回：
    1. "visible_context": 符合该查询的图片中可能包含的显性特征关键词（如特定的物体、颜色、场景元素，不超过100字）。
    2. "hidden_context": 符合该查询的图片可能传达的隐性特征关键词（如氛围、风格、情绪，不超过100字）。
    3. "description": 符合该查询的一张理想图片的完整画面描述（不超过500字）。
    注意：只返回合法的 JSON 格式，不要包含其他任何解释。
    """
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    print(f"  [文本模型] 正在呼叫 {TEXT_MODEL} 进行意图扩展和拆解...")
    text_features = call_chat_completion(messages, TEXT_MODEL)
    visible_text = text_features.get("visible_context", query) 
    hidden_text = text_features.get("hidden_context", query)
    description_text = text_features.get("description", query)

    print(f"  [扩写结果] 意图扩展完成：")
    print(f"    - 预期显性特征: {visible_text}")
    print(f"    - 预期隐性特征: {hidden_text}")
    print(f"    - 预期整体描述: {description_text}")

    print(f"\n▶ 步骤 2/2: 正在将预期特征文本转换为查询高维向量(1024维)...")
    return {
        "visible": {"vector": get_embedding(visible_text, "显性特征")},
        "hidden":  {"vector": get_embedding(hidden_text, "隐性特征")},
        "description": {"vector": get_embedding(description_text, "整体描述")}
    }
