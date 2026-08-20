import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HUGGINGFACE_HUB_CACHE"] = "./.cache/huggingface"

class SentenceTransformerEmbedding:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimensions = 384

    def load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            print(f"正在加载 SentenceTransformer 模型: {self.model_name}")
            print(f"使用镜像: {os.environ.get('HF_ENDPOINT')}")
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
