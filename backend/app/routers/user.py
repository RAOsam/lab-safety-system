from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import SessionLocal
from ..models import User
import hashlib

router = APIRouter(prefix="/api/user", tags=["用户"])

class UserCreate(BaseModel):
    username: str
    password: str

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(lambda: SessionLocal())):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = User(username=user.username, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    return {"msg": "注册成功"}