import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HUGGINGFACE_HUB_CACHE"] = "./.cache/huggingface"

import chromadb
from chromadb.config import Settings
from .config import CHROMA_PERSIST_DIR
from .embedding import SentenceTransformerEmbedding

class RAGEngine:
    def __init__(self):
        try:
            self.embedding_fn = SentenceTransformerEmbedding()
            self.client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name="lab_safety_knowledge"
            )
            print(f"成功连接到向量数据库: {CHROMA_PERSIST_DIR}")
            self.embedding_available = True
        except Exception as e:
            print(f"初始化RAG引擎失败: {e}")
            self.client = None
            self.collection = None
            self.embedding_available = False

    def retrieve(self, query: str, top_k: int = 5):
        if not self.collection:
            return []

        try:
            embedding = self.embedding_fn([query])[0]
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k
            )
            documents = results['documents'][0] if results['documents'] else []
            return documents
        except Exception as e:
            print(f"检索失败: {e}")
            return []

rag = RAGEngine()
