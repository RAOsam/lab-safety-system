from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import QARecord
from ..rag_engine import rag
from ..llm_client import ApiClient
from ..auth import get_current_user
import json

router = APIRouter(prefix="/api/qa", tags=["问答"])

class Question(BaseModel):
    user_id: int = None
    question: str

# 安全相关问题提示词模板 - 严肃严谨版本
SERIOUS_SAFETY_PROMPT_TEMPLATE = """你是一位专业的实验室安全专家。请根据以下参考资料回答用户问题。

参考资料：
{context}

用户问题：{question}

请严格按照以下格式回答：

隐患类型：
风险等级：
处置步骤：
预防建议：

要求：
1. 使用专业术语
2. 避免口语化表达
3. 提供具体的安全指导
4. 不要使用比喻或拟人化表达
5. 不要使用感叹号和表情符号
"""

# 闲聊提示词模板
CHAT_PROMPT_TEMPLATE = """你是一位友好的实验室安全助手。用户现在说："{question}"

如果这是打招呼、闲聊或与实验室安全无关的问题，请用自然、友好的语言回复。
如果这是实验室安全相关的问题，请按照以下格式回答：
隐患类型：xxx
风险等级：高/中/低
处置步骤：1. xxx 2. xxx ...
预防建议：xxx
"""

# 优化的关键词检测
GREETING_KEYWORDS = ["你好", "您好", "嗨", "Hello", "Hi", "早上好", "下午好", "晚上好", "拜拜", "再见", "谢谢", "感谢", "你是谁", "介绍一下"]

# 安全关键词列表
SAFETY_KEYWORDS = ["安全", "隐患", "风险", "危险", "泄漏", "火灾", "爆炸", "中毒", "腐蚀", "防护", "应急", "事故", "急救", "泄漏处理", "安全操作", "防护措施", "安全规程"]

# 设备相关关键词
EQUIPMENT_KEYWORDS = ["设备", "仪器", "仪器使用", "操作", "使用方法", "注意事项", "维护", "保养", "校准", "调试"]

def is_greeting(question: str) -> bool:
    """判断是否是打招呼或闲聊"""
    question_lower = question.lower().strip()
    for keyword in GREETING_KEYWORDS:
        if keyword.lower() in question_lower:
            return True
    return False

def is_safety_related(question: str) -> bool:
    """判断是否与实验室安全相关"""
    question_lower = question.lower()
    
    # 如果包含明显的危险词汇，认为是安全问题
    for keyword in SAFETY_KEYWORDS:
        if keyword in question_lower:
            return True
    
    # 如果包含设备操作相关词汇，也认为是安全问题
    for keyword in EQUIPMENT_KEYWORDS:
        if keyword in question_lower:
            return True
    
    return False

def clean_answer(answer: str) -> str:
    """清理回答，移除不相关内容和重复标题，保留格式"""
    # YOLO类别列表（用于过滤不相关检测结果）
    YOLO_CLASSES = set([
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
        'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
        'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
        'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
        'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
        'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
        'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
        'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
        'toothbrush', 'fire extinguisher', 'trash can'
    ])
    
    REQUIRED_SECTIONS = ['隐患类型：', '风险等级：', '处置步骤：', '预防建议：']
    
    lines = answer.split('\n')
    cleaned = []
    seen_sections = set()
    
    def is_yolo_line(line):
        """判断是否为YOLO检测结果行"""
        lower = line.lower()
        for cls in YOLO_CLASSES:
            if cls in lower:
                return True
        return False
    
    def is_confidence_line(line):
        """判断是否为置信度行（如 72.6%）"""
        return '%' in line and (line.strip().endswith('%') or ('(' in line and '%)' in line))
    
    def get_section_key(line):
        """提取行对应的章节键名"""
        for section in REQUIRED_SECTIONS:
            if line.strip().startswith(section.rstrip('：')):
                return section
        return None
    
    # 第一遍：过滤YOLO/置信度结果，去重章节标题
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if is_yolo_line(stripped) or is_confidence_line(stripped):
            continue
        if '检测到的物体' in stripped or 'detections' in stripped.lower():
            continue
        
        section_key = get_section_key(stripped)
        if section_key:
            if section_key in seen_sections:
                continue  # 跳过重复标题
            seen_sections.add(section_key)
        
        cleaned.append(stripped)
    
    if not cleaned:
        return answer
    
    # 第二遍：确保必要章节存在，补齐缺失
    result = '\n'.join(cleaned)
    missing = [s for s in REQUIRED_SECTIONS if s not in result]
    
    for section in missing:
        # 在最后一个已有的章节标题后插入
        for i, line in enumerate(cleaned):
            if get_section_key(line):
                # 检查是否后面已经有了缺失的章节
                has_after = False
                for j in range(i + 1, len(cleaned)):
                    if get_section_key(cleaned[j]):
                        break
                    if section in cleaned[j]:
                        has_after = True
                        break
                if not has_after:
                    result = result + '\n' + section
                    break
    
    return result

@router.post("/ask")
def ask(question: Question, db: Session = Depends(lambda: SessionLocal())):
    print(f"收到问答请求: {question.question}")
    
    # 判断是否是打招呼或闲聊
    if is_greeting(question.question):
        print("检测到打招呼，使用闲聊模式")
        llm_client = ApiClient()
        answer = llm_client.generate(CHAT_PROMPT_TEMPLATE.format(question=question.question))
        
        record = QARecord(
            user_id=question.user_id if question.user_id is not None else 1,
            question=question.question,
            answer=answer,
            risk_level="无"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return {"answer": answer, "risk_level": "无"}
    
    # 判断是否明显与安全无关
    if not is_safety_related(question.question):
        print("检测到非安全问题，使用闲聊模式")
        llm_client = ApiClient()
        answer = llm_client.generate(CHAT_PROMPT_TEMPLATE.format(question=question.question))
        
        record = QARecord(
            user_id=question.user_id if question.user_id is not None else 1,
            question=question.question,
            answer=answer,
            risk_level="无"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return {"answer": answer, "risk_level": "无"}
    
    # 安全相关问题，使用RAG流程
    # 1. 检索相关知识
    docs = rag.retrieve(question.question, top_k=5)
    context = "\n\n".join(docs) if docs else "无相关参考资料。"
    print(f"检索到 {len(docs)} 条相关知识")

    # 2. 构造提示词 - 使用严肃严谨的版本
    prompt = SERIOUS_SAFETY_PROMPT_TEMPLATE.format(question=question.question, context=context)
    print(f"提示词长度: {len(prompt)}")

    # 3. 调用大模型生成回答
    print("创建新的ApiClient实例...")
    llm_client = ApiClient()
    print(f"ApiClient提供商: {llm_client.provider}")
    print(f"ApiClient模型URL: {llm_client.api_base_url}")
    answer = llm_client.generate(prompt)
    
    # 4. 清理回答，移除不相关内容和重复标题
    answer = clean_answer(answer)
    print(f"清理后的回答: {answer[:400]}...")

    # 5. 解析风险等级（用于存储）
    risk = "中"
    if "风险等级：高" in answer:
        risk = "高"
    elif "风险等级：低" in answer:
        risk = "低"

    # 6. 保存到数据库
    record = QARecord(
        user_id=question.user_id if question.user_id is not None else 1,
        question=question.question,
        answer=answer,
        risk_level=risk
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"answer": answer, "risk_level": risk}

def generate_stream_response(prompt: str):
    """生成流式响应（使用 ApiClient 的配置）"""
    try:
        import requests
        from ..config import API_BASE_URL, API_KEY
        from ..llm_client import ApiClient
        
        # 使用 ApiClient 获取配置的模型名
        client = ApiClient()
        model_name = client._get_model_name()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=120
        )
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                    except json.JSONDecodeError:
                        continue
                        
    except Exception as e:
        print(f"流式响应生成失败: {e}")
        yield f"data: {json.dumps({'content': '抱歉，服务暂时不可用。'}, ensure_ascii=False)}\n\n"

@router.post("/ask/stream")
def ask_stream(question: Question, current_user: dict = Depends(get_current_user), db: Session = Depends(lambda: SessionLocal())):
    """流式问答接口"""
    print(f"收到流式问答请求: {question.question}")
    
    # 判断是否是打招呼或闲聊
    if is_greeting(question.question):
        prompt = CHAT_PROMPT_TEMPLATE.format(question=question.question)
    elif not is_safety_related(question.question):
        prompt = CHAT_PROMPT_TEMPLATE.format(question=question.question)
    else:
        # 安全相关问题，使用RAG流程
        docs = rag.retrieve(question.question, top_k=5)
        context = "\n\n".join(docs) if docs else "无相关参考资料。"
        prompt = SERIOUS_SAFETY_PROMPT_TEMPLATE.format(question=question.question, context=context)
    
    # 保存问答记录（空答案，后续会更新）
    record = QARecord(
        user_id=current_user["user_id"],
        question=question.question,
        answer="",
        risk_level="待分析"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # 返回流式响应
    return StreamingResponse(
        generate_stream_response(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )