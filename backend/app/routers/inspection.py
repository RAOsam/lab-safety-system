from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from ..database import SessionLocal
from ..models import InspectionRecord

router = APIRouter(prefix="/api/inspection", tags=["检查记录"])

class InspectionCreate(BaseModel):
    location: str
    inspector: str
    hazard_description: str
    risk_level: str
    responsible_person: str
    deadline: date

class InspectionUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None

@router.post("/create")
def create_record(record: InspectionCreate, db: Session = Depends(lambda: SessionLocal())):
    db_record = InspectionRecord(
        location=record.location,
        inspector=record.inspector,
        hazard_description=record.hazard_description,
        risk_level=record.risk_level,
        responsible_person=record.responsible_person,
        deadline=datetime.combine(record.deadline, datetime.min.time())
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/list")
def list_records(skip: int = 0, limit: int = 100, db: Session = Depends(lambda: SessionLocal())):
    records = db.query(InspectionRecord).offset(skip).limit(limit).all()
    return records

@router.put("/{record_id}")
def update_record(record_id: int, update: InspectionUpdate, db: Session = Depends(lambda: SessionLocal())):
    record = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    if update.status:
        record.status = update.status
    if update.completed_at:
        record.completed_at = update.completed_at
    db.commit()
    return record

@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(lambda: SessionLocal())):
    record = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"msg": "删除成功"}


# ===== 前端兼容路由（匹配前端 InspectionManage.vue 的调用方式） =====
# 前端调用: POST /api/inspections, GET /api/inspections, PUT /api/inspections/:id, DELETE /api/inspections/:id
# 前端字段: description, location, level, discovery_time, responsible_person, deadline

frontend_router = APIRouter(prefix="/api", tags=["检查记录(前端兼容)"])

class FrontendInspectionCreate(BaseModel):
    description: str
    location: str
    level: str  # low/medium/high
    discovery_time: datetime
    responsible_person: str
    deadline: date

@frontend_router.post("/inspections")
def frontend_create_record(record: FrontendInspectionCreate, db: Session = Depends(lambda: SessionLocal())):
    db_record = InspectionRecord(
        location=record.location,
        inspector=record.responsible_person,
        hazard_description=record.description,
        risk_level=record.level,
        responsible_person=record.responsible_person,
        deadline=datetime.combine(record.deadline, datetime.min.time())
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@frontend_router.get("/inspections")
def frontend_list_records(skip: int = 0, limit: int = 100, db: Session = Depends(lambda: SessionLocal())):
    records = db.query(InspectionRecord).offset(skip).limit(limit).all()
    # 转换为前端期望的格式
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "description": r.hazard_description,
            "location": r.location,
            "level": r.risk_level,
            "discovery_time": r.created_at.isoformat() if r.created_at else None,
            "responsible_person": r.responsible_person,
            "deadline": r.deadline.isoformat() if r.deadline else None,
            "status": "completed" if r.status == "已完成" or r.status == "completed" else "pending",
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return result

@frontend_router.put("/inspections/{record_id}")
def frontend_update_record(record_id: int, update: InspectionUpdate, db: Session = Depends(lambda: SessionLocal())):
    record = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    if update.status:
        record.status = "已完成" if update.status == "completed" else update.status
    if update.completed_at:
        record.completed_at = update.completed_at
    db.commit()
    return {"msg": "更新成功"}

@frontend_router.delete("/inspections/{record_id}")
def frontend_delete_record(record_id: int, db: Session = Depends(lambda: SessionLocal())):
    record = db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"msg": "删除成功"}