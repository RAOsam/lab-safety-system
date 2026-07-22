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
except Exception as e:
    print(f"加载YOLO模型失败 ({YOLO_MODEL_PATH}): {e}")
    import os
    fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "yolov8n.pt")
    print(f"尝试加载备用路径: {fallback_path}")
    yolo_model = YOLO(fallback_path)

# 类别名称中英文映射
CLASS_NAME_MAP = {
    'person': '人员',
    'bottle': '瓶子/容器',
    'wine glass': '玻璃器皿',
    'cup': '杯子',
    'bowl': '碗',
    'fork': '叉子',
    'knife': '刀具',
    'spoon': '勺子',
    'scissors': '剪刀',
    'chair': '椅子',
    'bench': '长椅',
    'couch': '沙发',
    'dining table': '桌子',
    'tv': '显示器',
    'tv_monitor': '显示器',
    'laptop': '笔记本电脑',
    'mouse': '鼠标',
    'keyboard': '键盘',
    'cell phone': '手机',
    'microwave': '微波炉',
    'oven': '烤箱',
    'toaster': '烤面包机',
    'refrigerator': '冰箱',
    'sink': '水槽',
    'fire extinguisher': '灭火器',
    'trash can': '垃圾桶',
    'book': '书籍/文件',
    'clock': '时钟',
    'vase': '花瓶',
    'backpack': '背包',
    'handbag': '手提包',
    'umbrella': '雨伞',
    'tie': '领带',
    'suitcase': '行李箱',
    'potted plant': '盆栽植物',
    'bed': '床',
    'hair drier': '吹风机',
    'toothbrush': '牙刷',
    'remote': '遥控器',
    'cake': '蛋糕',
    'sandwich': '三明治',
    'apple': '苹果',
    'orange': '橙子',
    'banana': '香蕉',
    'carrot': '胡萝卜',
    'broccoli': '西兰花',
    'hot dog': '热狗',
    'pizza': '披萨',
    'donut': '甜甜圈',
}

CONFIDENCE_THRESHOLD = 0.3

# 实验室安全相关类别（使用英文名匹配YOLO输出）
LAB_CATEGORIES = {
    'person', 'bottle', 'wine glass', 'cup', 'bowl', 'fork', 'knife', 'spoon',
    'scissors', 'chair', 'bench', 'couch', 'dining table',
    'tv', 'tv_monitor', 'laptop', 'mouse', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'refrigerator', 'sink',
    'fire extinguisher', 'trash can',
    'book', 'clock', 'vase', 'backpack', 'handbag', 'umbrella', 'tie', 'suitcase',
    'potted plant', 'bed', 'hair drier', 'toothbrush', 'remote',
    'cake', 'sandwich', 'apple', 'orange', 'banana', 'carrot', 'broccoli',
    'hot dog', 'pizza', 'donut',
}

def analyze_hazards_with_llm(detections):
    """使用LLM分析检测到的物体，推断安全隐患"""
    detected_objects = [d['class'] for d in detections]
    objects_str = "、".join(detected_objects) if detected_objects else "未检测到特定物体"
    
    prompt = f"""你是一个实验室安全专家。在实验室场景的照片中检测到了以下物体：{objects_str}

请根据这些物体分析可能存在的实验室安全隐患，**重点分析以下方面**：

### 一、用电安全与插座/插板管理（重中之重）
- 检测到"显示器"、"笔记本电脑"、"微波炉"、"烤箱"、"烤面包机"、"吹风机"、"冰箱"等电器时：
  - **推断插座/插板可能存在的问题**：多个大功率电器共用一个插板可能导致**过载发热**；电线杂乱拖地可能绊倒或磨损漏电；电器靠近水槽存在触电风险
  - 检查电器是否**长时间通电无人看管**
  - 检查电线是否被桌椅挤压导致绝缘层破损
- 即使没有检测到电器，也要注意：实验室中常见的**插座/插板安全隐患**包括：
  - 插座被实验台或家具遮挡，难以紧急断电
  - 插板放在地面上容易被液体溅到导致短路
  - 电线穿过通道区域可能被踩踏磨损
  - 插座附近堆放易燃物品

### 二、化学品安全
- 检测到"瓶子/容器"、"玻璃器皿"时：检查化学品是否分类存放、有明确标签、远离热源和电源
- 检测到"冰箱"时：检查化学品与食品是否混放
- 检测到"水槽"时：检查废液处理是否规范

### 三、消防安全
- 检测到"灭火器"时：检查是否被遮挡、是否在有效期内
- 检测到"垃圾桶"时：检查是否堆积易燃废料

### 四、通道与布局安全
- 检测到"椅子"、"沙发"、"长椅"、"垃圾桶"等时：检查是否阻塞安全通道
- 检测到"床"时：实验室不应有床铺

### 五、个人安全与行为规范
- 检测到"人员"时：检查是否佩戴护目镜、实验服
- 检测到"杯子"、"碗"、"蛋糕"等食物或餐具时：实验区域禁止饮食
- 检测到"刀具"、"剪刀"时：检查锐器是否妥善保管

请直接输出安全隐患要点，每条一行，以"- "开头，最多3条。
如果没有明显安全隐患，请只输出"未发现明显安全隐患"。
"""

    try:
        llm_client = ApiClient()
        result = llm_client.generate(prompt, max_new_tokens=512)
        
        hazards = []
        for line in result.strip().split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                hazards.append(line[2:])
        
        if not hazards:
            hazards = ["未发现明显安全隐患，请继续保持"]
        return hazards[:3]
    except Exception as e:
        print(f"LLM分析失败: {e}")
        return simple_hazard_inference(detections)

def simple_hazard_inference(detections):
    """简单的规则推理（作为LLM的降级方案）"""
    hazards = []
    detected_classes = set()
    
    for det in detections:
        cls = det['class']
        if cls in detected_classes:
            continue
        detected_classes.add(cls)
        
        # === 用电安全与插座/插板管理 ===
        if cls in ['显示器', '笔记本电脑', 'tv', 'laptop', 'tv_monitor']:
            hazards.append("电器设备需检查插板是否过载、电线是否杂乱拖地、是否靠近水源，长时间不用需断电")
        elif cls in ['微波炉', '烤箱', 'microwave', 'oven']:
            hazards.append("大功率加热设备需使用专用插座，避免与其他电器共用插板导致过载，使用后及时断电")
        elif cls in ['烤面包机', 'toaster']:
            hazards.append("烤面包机功率较大，需单独使用插座，远离易燃物，使用后及时拔掉电源")
        elif cls in ['吹风机', 'hair drier']:
            hazards.append("吹风机需远离水源使用，插板应配备漏电保护，使用后及时拔掉电源")
        elif cls in ['冰箱', 'refrigerator']:
            hazards.append("冰箱需使用独立插座，确保接地良好，周围保持通风散热，禁止食品与化学品混放")
        elif cls in ['手机', 'cell phone']:
            hazards.append("实验区域内禁止使用手机充电，充电器长期插在插板上存在火灾隐患")
        
        # === 化学品安全 ===
        elif cls in ['瓶子/容器', 'bottle']:
            hazards.append("化学品容器需有明确标签，分类存放，远离热源和电源插板")
        elif cls in ['玻璃器皿', 'wine glass']:
            hazards.append("玻璃器皿易碎，使用时应戴防护手套，破损后需妥善处理")
        elif cls in ['水槽', 'sink']:
            hazards.append("水槽区域应配备洗眼器，废液需按规定分类处理，禁止直接倒入下水道")
        
        # === 消防安全 ===
        elif cls in ['灭火器', 'fire extinguisher']:
            hazards.append("灭火器需定期检查压力表，确保在有效期内，周围不得堆放杂物遮挡")
        elif cls in ['垃圾桶', 'trash can']:
            hazards.append("垃圾桶需及时清理，易燃废料（如纸巾、包装纸）不得堆积过多")
        
        # === 通道安全 ===
        elif cls in ['椅子', '沙发', '长椅', 'chair', 'couch', 'bench']:
            hazards.append("家具不得阻塞安全通道和紧急出口，保持通道畅通")
        elif cls in ['床', 'bed']:
            hazards.append("实验室内严禁放置床铺，存在严重安全隐患")
        
        # === 行为规范 ===
        elif cls == '人员':
            hazards.append("人员未佩戴护目镜或实验服（需进一步确认）")
        elif cls in ['刀具', '剪刀', 'knife', 'scissors']:
            hazards.append("锐器需妥善保管，使用后放回专用容器，避免划伤")
        elif cls in ['杯子', '碗', 'cup', 'bowl', '蛋糕', 'cake', '三明治', 'sandwich', '苹果', 'apple', '橙子', 'orange', '香蕉', 'banana', '披萨', 'pizza', '热狗', 'hot dog', '甜甜圈', 'donut']:
            hazards.append("实验区域禁止饮食，食物和餐具不得带入实验室")
    
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
        
        if conf < CONFIDENCE_THRESHOLD:
            continue
        
        if cls not in LAB_CATEGORIES:
            print(f"过滤掉不相关类别: {cls} ({conf:.2f})")
            continue
        
        if cls not in seen_classes or conf > seen_classes[cls]['confidence']:
            seen_classes[cls] = {
                'class': CLASS_NAME_MAP.get(cls, cls),
                'confidence': conf
            }
    
    cleaned = sorted(seen_classes.values(), key=lambda x: -x['confidence'])
    return cleaned

@router.post("/inspect")
async def inspect_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # YOLO检测
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

    # 清理检测结果
    cleaned_detections = clean_detections(detections)
    print(f"YOLO检测到 {len(detections)} 个物体，清理后 {len(cleaned_detections)} 个")

    # 使用LLM分析安全隐患（即使没有检测到物体也会分析）
    hazards = analyze_hazards_with_llm(cleaned_detections)

    # 为每个隐患生成处置建议
    suggestions = []
    for hazard in hazards[:3]:
        if "未发现" in hazard:
            continue
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
        advice = llm_client.generate(prompt, max_new_tokens=512)
        suggestions.append({"hazard": hazard, "advice": advice})

    return {
        "has_hazard": len([h for h in hazards if "未发现" not in h]) > 0,
        "detections": cleaned_detections,
        "hazards": hazards,
        "suggestions": suggestions
    }