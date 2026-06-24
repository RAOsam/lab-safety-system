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

class UserResponse(BaseModel):
    id: int
    username: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

@router.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(lambda: SessionLocal())):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = User(username=user.username, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "注册成功", "user": {"id": new_user.id, "username": new_user.username}}

@router.post("/login", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(lambda: SessionLocal())):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or user.password_hash != hash_password(request.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    return {"msg": "登录成功", "user": {"id": user.id, "username": user.username}}

@router.get("/list", response_model=list[UserResponse])
def get_user_list(db: Session = Depends(lambda: SessionLocal())):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username} for u in users]

@router.put("/{user_id}/password", response_model=dict)
def change_password(
    user_id: int,
    request: ChangePasswordRequest,
    db: Session = Depends(lambda: SessionLocal())
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.password_hash != hash_password(request.old_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    user.password_hash = hash_password(request.new_password)
    db.commit()
    return {"msg": "密码修改成功"}

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(lambda: SessionLocal())):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return {"msg": "删除成功"}