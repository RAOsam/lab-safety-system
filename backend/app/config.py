import os
from dotenv import load_dotenv
from pathlib import Path

# 获取当前文件所在目录的路径
current_dir = Path(__file__).resolve().parent

# 加载 .env 文件（位于 backend 目录下）
env_path = current_dir.parent / ".env"
print(f"尝试加载环境变量文件: {env_path}")
print(f"文件是否存在: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)
print(f"加载后 API_BASE_URL: {os.getenv('API_BASE_URL')}")

MODEL_PATH = os.getenv("MODEL_PATH")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR")
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR")
MYSQL_URL = os.getenv("MYSQL_URL")
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "./models/yolov8n.pt")

# API 配置
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.together.xyz")
API_KEY = os.getenv("API_KEY", "")