import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HUGGINGFACE_HUB_CACHE"] = "./.cache/huggingface"

import json
import chromadb

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

class DatasetLoader:
    def __init__(self):
        self.embedding_fn = SentenceTransformerEmbedding()
    
    def init_chroma(self, persist_dir: str = "../data/vector_db"):
        from chromadb.config import Settings
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="lab_safety_knowledge"
        )
    
    def load_huggingface_dataset(self, dataset_name: str = "yujunzhou/LabSafety_Bench"):
        try:
            from datasets import load_dataset
            print(f"正在从 Hugging Face 镜像加载数据集: {dataset_name}")
            print(f"使用镜像: {os.environ.get('HF_ENDPOINT')}")
            
            combined_data = []
            
            dataset_mcq = load_dataset(dataset_name, name="MCQ", split="QA")
            print(f"MCQ数据集加载成功，共 {len(dataset_mcq)} 条记录")
            for item in dataset_mcq:
                combined_data.append({
                    "question": item.get("Question", ""),
                    "answer": item.get("Explanation", "") + "\n正确答案: " + item.get("Correct Answer", ""),
                    "context": "; ".join(item.get("Category", [])) + " | " + item.get("Topic", "")
                })
            
            dataset_scenario = load_dataset(dataset_name, name="scenario", split="scenario")
            print(f"scenario数据集加载成功，共 {len(dataset_scenario)} 条记录")
            for item in dataset_scenario:
                combined_data.append({
                    "question": item.get("Question", ""),
                    "answer": item.get("Answer", "") if "Answer" in item else item.get("Explanation", ""),
                    "context": item.get("Scenario", "") if "Scenario" in item else ""
                })
            
            print(f"合并后共 {len(combined_data)} 条记录")
            return combined_data
            
        except Exception as e:
            print(f"加载数据集失败: {e}")
            return None
    
    def load_local_json(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"本地文件加载成功，共 {len(data)} 条记录")
            return data
        except Exception as e:
            print(f"加载本地文件失败: {e}")
            return None
    
    def import_to_chroma(self, data):
        if data is None or len(data) == 0:
            print("数据为空，无法导入")
            return 0
        
        self.init_chroma()
        
        print(f"开始生成嵌入向量，共 {len(data)} 条记录...")
        
        contents = []
        for item in data:
            question = item.get("question", "")
            answer = item.get("answer", "")
            context = item.get("context", "")
            content = f"问题: {question}\n答案: {answer}\n上下文: {context}".strip()
            contents.append(content)
        
        embeddings = self.embedding_fn(contents)
        
        count = 0
        for idx, (content, embedding) in enumerate(zip(contents, embeddings)):
            try:
                self.collection.add(
                    documents=[content],
                    ids=[f"lab_safety_{idx}"],
                    embeddings=[embedding]
                )
                count += 1
                
                if (idx + 1) % 100 == 0:
                    print(f"已导入 {idx + 1} 条记录")
            except Exception as e:
                print(f"导入第 {idx} 条记录失败: {e}")
        
        print(f"导入完成，共成功导入 {count} 条记录")
        return count
    
    def clear_collection(self):
        try:
            self.init_chroma()
            self.client.delete_collection("lab_safety_knowledge")
            print("已清空向量数据库")
        except Exception as e:
            print(f"清空失败: {e}")
    
    def get_collection_stats(self):
        try:
            self.init_chroma()
            count = self.collection.count()
            print(f"向量数据库中共有 {count} 条记录")
            return count
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return 0
    
    def add_sample_data(self):
        sample_data = [
            {
                "question": "浓硫酸溅到皮肤怎么办？",
                "answer": "1. 立即用大量流动清水冲洗皮肤至少15分钟；2. 脱去污染的衣物；3. 不要用中和剂；4. 及时就医。",
                "context": "化学实验室安全操作规程"
            },
            {
                "question": "如何正确使用酒精灯？",
                "answer": "1. 检查灯芯和酒精量；2. 用火柴点燃，禁止用另一盏酒精灯引燃；3. 加热时用外焰；4. 熄灭时用灯帽盖灭，不要用嘴吹。",
                "context": "实验室常用设备使用规范"
            },
            {
                "question": "实验废液如何处理？",
                "answer": "1. 根据废液性质分类收集；2. 倒入指定的废液桶；3. 不得随意倾倒；4. 做好记录。",
                "context": "实验室废弃物管理规定"
            },
            {
                "question": "发生火灾时应怎么办？",
                "answer": "1. 保持冷静；2. 拨打火警电话；3. 使用灭火器灭火；4. 疏散到安全区域；5. 关闭电源和气源。",
                "context": "实验室应急预案"
            },
            {
                "question": "如何正确佩戴个人防护装备？",
                "answer": "1. 实验前检查装备完整性；2. 佩戴护目镜、手套、实验服；3. 长发束起；4. 禁止佩戴首饰。",
                "context": "个人防护装备使用指南"
            },
            {
                "question": "高压气瓶如何安全存放？",
                "answer": "1. 存放在通风良好的专用气瓶柜；2. 固定防止倾倒；3. 远离热源和火源；4. 氧气瓶和乙炔瓶分开存放。",
                "context": "高压气体安全管理规定"
            },
            {
                "question": "触电急救方法是什么？",
                "answer": "1. 立即切断电源；2. 用绝缘物体将触电者与电源分离；3. 检查呼吸和心跳；4. 进行心肺复苏并拨打急救电话。",
                "context": "电气安全操作规程"
            },
            {
                "question": "如何处理化学试剂泄漏？",
                "answer": "1. 疏散人员；2. 穿戴防护装备；3. 用吸附材料吸收泄漏物；4. 按照化学品MSDS进行处理；5. 报告主管人员。",
                "context": "化学品泄漏应急处理"
            },
            {
                "question": "实验结束后应做哪些工作？",
                "answer": "1. 关闭所有电源和燃气；2. 清理实验台面；3. 归还试剂和仪器；4. 做好实验记录；5. 检查安全设施。",
                "context": "实验室日常管理规范"
            },
            {
                "question": "如何正确储存化学试剂？",
                "answer": "1. 分类存放（酸、碱、氧化剂、还原剂分开）；2. 避光、防潮、通风；3. 易燃品远离火源；4. 标签清晰；5. 定期检查。",
                "context": "化学试剂储存管理规定"
            }
        ]
        return self.import_to_chroma(sample_data)

def main():
    loader = DatasetLoader()
    print("=== 当前向量数据库状态 ===")
    loader.get_collection_stats()
    
    print("\n=== 尝试从 Hugging Face 镜像导入数据集 ===")
    data = loader.load_huggingface_dataset("yujunzhou/LabSafety_Bench")
    
    if data:
        print("\n=== 清空旧数据 ===")
        loader.clear_collection()
        print("\n=== 导入新数据 ===")
        loader.import_to_chroma(data)
    else:
        print("Hugging Face 数据集导入失败，使用示例数据")
        loader.add_sample_data()
    
    print("\n=== 导入后状态 ===")
    loader.get_collection_stats()

if __name__ == "__main__":
    main()