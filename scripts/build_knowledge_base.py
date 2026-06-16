import os
import glob
from PyPDF2 import PdfReader
from docx import Document
import chromadb
from chromadb.utils import embedding_functions

KNOWLEDGE_DIR = "./data/knowledge"
CHROMA_PERSIST_DIR = "./data/vector_db"
EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"

def read_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".pdf":
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        elif ext == ".docx":
            doc = Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            return ""
    except Exception as e:
        print(f"读取文件 {filepath} 出错: {e}")
        return ""

def chunk_text(text, chunk_size=500, overlap=50):
    import re
    # 清除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 分句（保留句末标点）
    sentences = re.split(r'(?<=[。！？；])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # 超长句子单独切分
        if len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            start = 0
            while start < len(sentence):
                end = min(start + chunk_size, len(sentence))
                chunks.append(sentence[start:end])
                start += chunk_size - overlap
            continue

        # 正常拼接
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def main():
    # 初始化 Chroma 客户端
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    
    # 如果集合已存在，先删除（可选）
    try:
        client.delete_collection("lab_safety_knowledge")
    except:
        pass
    collection = client.create_collection(name="lab_safety_knowledge", embedding_function=embed_fn)

    all_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.*"), recursive=True)
    if not all_files:
        print(f"警告: {KNOWLEDGE_DIR} 目录下没有找到任何文件")
        return

    doc_id = 0
    for filepath in all_files:
        text = read_text_from_file(filepath)
        if not text:
            continue
        chunks = chunk_text(text)
        for chunk in chunks:
            collection.add(
                documents=[chunk],
                ids=[f"doc_{doc_id}"],
                metadatas=[{"source": os.path.basename(filepath)}]
            )
            doc_id += 1
    print(f"知识库构建完成，共添加 {doc_id} 个文本片段")

if __name__ == "__main__":
    main()