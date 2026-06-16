import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HUGGINGFACE_HUB_CACHE"] = "./.cache/huggingface"

import chromadb
from chromadb.config import Settings
from .config import CHROMA_PERSIST_DIR

class SentenceTransformerEmbedding:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimensions = 384
    
    def load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            print(f"正在加载 SentenceTransformer 模型: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.dimensions = self.model.get_sentence_embedding_dimension()
            print(f"模型加载成功，向量维度: {self.dimensions}")
            return True
        except Exception as e:
            print(f"加载 SentenceTransformer 模型失败: {e}")
            return False
    
    def __call__(self, input):
        if self.model is None:
            if not self.load_model():
                return self._fallback_embedding(input)
        
        try:
            embeddings = self.model.encode(input)
            return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
        except Exception as e:
            print(f"生成嵌入失败，使用备用方案: {e}")
            return self._fallback_embedding(input)
    
    def _fallback_embedding(self, input):
        results = []
        for text in input:
            if isinstance(text, str):
                hash_val = hash(text)
                embedding = [(hash_val * (i + 1)) % 1000 / 1000 for i in range(self.dimensions)]
            else:
                embedding = [0.0] * self.dimensions
            results.append(embedding)
        return results

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