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

# 类别名称中英文映射
CLASS_NAME_MAP = {
    'person': '人物',
    'bicycle': '自行车',
    'car': '汽车',
    'motorcycle': '摩托车',
    'airplane': '飞机',
    'bus': '公交车',
    'train': '火车',
    'truck': '卡车',
    'boat': '船',
    'traffic light': '交通灯',
    'fire hydrant': '消防栓',
    'stop sign': '停止标志',
    'parking meter': '停车计时器',
    'bench': '长椅',
    'bird': '鸟',
    'cat': '猫',
    'dog': '狗',
    'horse': '马',
    'sheep': '羊',
    'cow': '牛',
    'elephant': '大象',
    'bear': '熊',
    'zebra': '斑马',
    'giraffe': '长颈鹿',
    'backpack': '背包',
    'umbrella': '雨伞',
    'handbag': '手提包',
    'tie': '领带',
    'suitcase': '行李箱',
    'frisbee': '飞盘',
    'skis': '滑雪板',
    'snowboard': '滑雪板',
    'sports ball': '运动球',
    'kite': '风筝',
    'baseball bat': '棒球棒',
    'baseball glove': '棒球手套',
    'skateboard': '滑板',
    'surfboard': '冲浪板',
    'tennis racket': '网球拍',
    'bottle': '瓶子',
    'wine glass': '酒杯',
    'cup': '杯子',
    'fork': '叉子',
    'knife': '刀',
    'spoon': '勺子',
    'bowl': '碗',
    'banana': '香蕉',
    'apple': '苹果',
    'sandwich': '三明治',
    'orange': '橙子',
    'broccoli': '西兰花',
    'carrot': '胡萝卜',
    'hot dog': '热狗',
    'pizza': '披萨',
    'donut': '甜甜圈',
    'cake': '蛋糕',
    'chair': '椅子',
    'couch': '沙发',
    'potted plant': '盆栽植物',
    'bed': '床',
    'dining table': '餐桌',
    'toilet': '厕所',
    'tv': '电视',
    'laptop': '笔记本电脑',
    'mouse': '鼠标',
    'remote': '遥控器',
    'keyboard': '键盘',
    'cell phone': '手机',
    'microwave': '微波炉',
    'oven': '烤箱',
    'toaster': '烤面包机',
    'sink': '水槽',
    'refrigerator': '冰箱',
    'book': '书',
    'clock': '时钟',
    'vase': '花瓶',
    'scissors': '剪刀',
    'teddy bear': '泰迪熊',
    'hair drier': '吹风机',
    'toothbrush': '牙刷',
    'fire extinguisher': '灭火器',
    'trash can': '垃圾桶',
    'tv_monitor': '显示器'
}

CONFIDENCE_THRESHOLD = 0.5  # 置信度阈值，提高到0.5减少误检

# 实验室常见物体类别（过滤掉不相关的类别如冲浪板、滑雪板等）
LAB_CATEGORIES = {
    'person', 'bottle', 'chair', 'laptop', 'tv', 'tv_monitor', 'mouse', 'keyboard',
    'cell phone', 'microwave', 'oven', 'refrigerator', 'book', 'clock', 'vase',
    'scissors', 'fire extinguisher', 'trash can', 'desk', 'table', 'bench',
    'backpack', 'handbag', 'cup', 'bowl', 'fork', 'knife', 'spoon', 'bed',
    'couch', 'potted plant', 'toilet', 'sink', 'dining table', 'baseball bat',
    'sports ball', 'umbrella', 'tie', 'suitcase', 'frisbee', 'kite', 'remote',
    'hair drier', 'toothbrush', 'teddy bear', 'car', 'truck', 'bus', 'motorcycle',
    'bicycle', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter',
    'bird', 'cat', 'dog', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
    'horse', 'airplane', 'train', 'boat'
}

def simple_hazard_inference(detections):
    hazards = []
    detected_classes = set()
    
    for det in detections:
        cls = det['class']
        if cls in detected_classes:
            continue
        detected_classes.add(cls)
        
        if cls == 'person':
            hazards.append("人员未佩戴护目镜（需进一步确认）")
        elif cls == 'fire extinguisher':
            hazards.append("灭火器可能存在遮挡或放置不当")
        elif cls == 'bottle':
            hazards.append("化学品容器需有明确标签并分类存放")
        elif cls == 'chair' or cls == 'trash can':
            hazards.append("物品阻塞安全通道或出口")
        elif cls == 'tv' or cls == 'tv_monitor' or cls == 'laptop':
            hazards.append("电器设备长时间通电，注意过热")
    
    if not hazards:
        hazards.append("未发现明显安全隐患，请继续保持")
    return hazards

def clean_detections(detections):
    """清理检测结果：去重、过滤不相关类别并转换为中文"""
    seen_classes = {}
    cleaned = []
    
    for det in detections:
        cls = det['class']
        conf = det['confidence']
        
        # 过滤低置信度
        if conf < CONFIDENCE_THRESHOLD:
            continue
        
        # 过滤实验室不常见的类别（如冲浪板、滑雪板等）
        if cls not in LAB_CATEGORIES:
            print(f"过滤掉不相关类别: {cls} ({conf:.2f})")
            continue
        
        # 去重：保留同一类别的最高置信度
        if cls not in seen_classes or conf > seen_classes[cls]['confidence']:
            seen_classes[cls] = {
                'class': CLASS_NAME_MAP.get(cls, cls),  # 转换为中文
                'confidence': conf
            }
    
    # 转换为列表并按置信度排序
    cleaned = sorted(seen_classes.values(), key=lambda x: -x['confidence'])
    return cleaned

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

    # 清理检测结果：去重、过滤低置信度、转换中文
    cleaned_detections = clean_detections(detections)
    print(f"清理前检测到 {len(detections)} 个物体，清理后 {len(cleaned_detections)} 个")

    hazards = simple_hazard_inference(detections)

    suggestions = []
    for hazard in hazards[:3]:
        docs = rag.retrieve(hazard, top_k=3)
        context = "\n".join(docs) if docs else "无相关资料"
        prompt = f"""实验室安全专家，针对以下隐患提供详细的处置建议和预防措施。

隐患：{hazard}
参考资料：{context}

请按照以下格式输出完整内容：
处置步骤：
1. ...
2. ...
3. ...

预防建议：
- ...
- ...
- ...

确保内容完整，步骤清晰。
"""
        llm_client = ApiClient()
        advice = llm_client.generate(prompt, max_new_tokens=512)  # 增加token数量
        suggestions.append({"hazard": hazard, "advice": advice})

    return {
        "has_hazard": len([h for h in hazards if "未发现" not in h]) > 0,
        "detections": cleaned_detections,  # 使用清理后的检测结果
        "hazards": hazards,
        "suggestions": suggestions
    }