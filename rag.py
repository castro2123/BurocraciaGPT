import os
os.environ["HF_HUB_OFFLINE"] = "1"

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import *

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"local_files_only": True}
)

db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)

def search(query, k=TOP_K):

    results = db.similarity_search_with_score(query, k=k)

    if not results:
        return [], 0.0, []

    docs, scores = zip(*results)

    best_score = min(scores)

    confidence = max(0.0, min(1.0, 1 / (1 + best_score)))

    debug_info = [
        {
            "text": d.page_content[:200],
            "score": float(s)
        }
        for d, s in zip(docs, scores)
    ]

    return list(docs), confidence, debug_info