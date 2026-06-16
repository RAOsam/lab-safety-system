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

class CohereEmbedding:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("COHERE_API_KEY")
        self.dimensions = 768
    
    def __call__(self, input):
        try:
            import cohere
            co = cohere.Client(self.api_key)
            response = co.embed(texts=input, model="embed-english-v3.0")
            return response.embeddings
        except Exception as e:
            print(f"Cohere API调用失败，使用备用方案: {e}")
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

class FastTextEmbedding:
    def __init__(self):
        self.model = None
        self.dimensions = 300
    
    def load_model(self):
        try:
            import fasttext
            import fasttext.util
            fasttext.util.download_model('zh', if_exists='ignore')
            self.model = fasttext.load_model('cc.zh.300.bin')
            print("FastText 模型加载成功")
            return True
        except Exception as e:
            print(f"加载 FastText 模型失败: {e}")
            return False
    
    def __call__(self, input):
        if self.model is None:
            if not self.load_model():
                return self._fallback_embedding(input)
        
        try:
            results = []
            for text in input:
                if isinstance(text, str):
                    embedding = self.model.get_sentence_vector(text).tolist()
                else:
                    embedding = [0.0] * self.dimensions
                results.append(embedding)
            return results
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

def get_embedding_function(embedding_type: str = "sentence_transformer"):
    embedding_functions = {
        "sentence_transformer": SentenceTransformerEmbedding(),
        "cohere": CohereEmbedding(),
        "fasttext": FastTextEmbedding(),
    }
    return embedding_functions.get(embedding_type, SentenceTransformerEmbedding())