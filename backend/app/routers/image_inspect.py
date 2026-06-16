from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import cv2
import numpy as np
import os

# 设置环境变量解决PyTorch 2.6+的安全限制
os.environ['TORCH_LOAD_WEIGHTS_ONLY'] = '0'

from ultralytics import YOLO
from ..config import YOLO_MODEL_PATH
from ..llm_client import ApiClient
from ..rag_engine import rag

router = APIRouter(prefix="/api/image", tags=["图像识别"])

# 加载YOLO模型
try:
    yolo_model = YOLO(YOLO_MODEL_PATH)
except:
    yolo_model = YOLO("yolov8n.pt")  # 自动下载

def simple_hazard_inference(detections):
    hazards = []
    for det in detections:
        cls = det['class']
        if cls == 'person':
            hazards.append("人员未佩戴护目镜（需进一步确认）")
        elif cls == 'fire extinguisher':
            hazards.append("灭火器可能存在遮挡或放置不当")
        elif cls == 'bottle':
            hazards.append("化学品容器需有明确标签并分类存放")
        elif cls == 'chair' or cls == 'trash can':
            hazards.append("物品阻塞安全通道或出口")
        elif cls == 'tv_monitor' or cls == 'laptop':
            hazards.append("电器设备长时间通电，注意过热")
    if not hazards:
        hazards.append("未发现明显安全隐患，请继续保持")
    return hazards

@router.post("/inspect")
async def inspect_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    results = yolo_model(img_cv, verbose=False)
    detections = []
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = yolo_model.names[cls]
                detections.append({"class": class_name, "confidence": conf})

    hazards = simple_hazard_inference(detections)

    suggestions = []
    for hazard in hazards[:3]:
        docs = rag.retrieve(hazard, top_k=3)
        context = "\n".join(docs) if docs else "无相关资料"
        prompt = f"""实验室安全专家，针对以下隐患提供具体处置建议和预防措施。
隐患：{hazard}
参考资料：{context}
输出格式：
处置步骤：1. ... 2. ...
预防建议：...
"""
        llm_client = ApiClient()
        advice = llm_client.generate(prompt, max_new_tokens=300)
        suggestions.append({"hazard": hazard, "advice": advice})

    return {
        "has_hazard": len([h for h in hazards if "未发现" not in h]) > 0,
        "detections": detections,
        "hazards": hazards,
        "suggestions": suggestions
    }