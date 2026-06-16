from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import QARecord
from ..rag_engine import rag
from ..llm_client import ApiClient

router = APIRouter(prefix="/api/qa", tags=["问答"])

class Question(BaseModel):
    user_id: int = None
    question: str

PROMPT_TEMPLATE = """你是一位实验室安全专家。请根据以下参考资料回答用户问题，并严格按照格式输出。

参考资料：
{context}

用户问题：{question}

输出格式（必须严格遵守，不要添加额外内容）：
隐患类型：xxx
风险等级：高/中/低
处置步骤：1. xxx 2. xxx ...
预防建议：xxx
"""

@router.post("/ask")
def ask(question: Question, db: Session = Depends(lambda: SessionLocal())):
    print(f"收到问答请求: {question.question}")
    
    # 1. 检索相关知识
    docs = rag.retrieve(question.question, top_k=5)
    context = "\n\n".join(docs) if docs else "无相关参考资料。"
    print(f"检索到 {len(docs)} 条相关知识")

    # 2. 构造提示词
    prompt = PROMPT_TEMPLATE.format(context=context, question=question.question)
    print(f"提示词长度: {len(prompt)}")

    # 3. 调用大模型生成回答
    print("创建新的ApiClient实例...")
    llm_client = ApiClient()
    print(f"ApiClient提供商: {llm_client.provider}")
    print(f"ApiClient模型URL: {llm_client.api_base_url}")
    answer = llm_client.generate(prompt)

    # 4. 解析风险等级（用于存储）
    risk = "中"
    if "风险等级：高" in answer:
        risk = "高"
    elif "风险等级：低" in answer:
        risk = "低"

    # 5. 保存到数据库
    record = QARecord(
        user_id=question.user_id,
        question=question.question,
        answer=answer,
        risk_level=risk
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"answer": answer, "risk_level": risk}