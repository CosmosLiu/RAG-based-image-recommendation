from pydantic import BaseModel
from typing import List

class SaveImageRequest(BaseModel):
    uid: str
    image_url: str

class TextRecommendRequest(BaseModel):
    uid: str
    query: str
    top_k: int = 10

class ImageRecommendRequest(BaseModel):
    uid: str
    image_url: str
    top_k: int = 10

class RecommendResponse(BaseModel):
    results: List[str]
