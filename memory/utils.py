import numpy as np
import os
import httpx
def cosine_similarity(a:list[float],b:list[float]):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

async def get_embedding(text:str):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    header = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    url = "https://api.openai.com/v1/embeddings"
    data = {
        "model": "text-embedding-3-small",
        "input": text
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url,headers=header,json=data)
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
    except Exception as e:
        return None
