from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import SessionLocal
from ..models import User, UserRole
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, get_admin_user
from datetime import timedelta

router = APIRouter(prefix="/api/user", tags=["用户"])

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str = None
    lab_name: str = None
    phone: str = None
    email: str = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str = None
    lab_name: str = None
    role: str = None

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(lambda: SessionLocal())):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    new_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        lab_name=user.lab_name,
        phone=user.phone,
        email=user.email,
        role=UserRole.USER
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "注册成功", "user": {"id": new_user.id, "username": new_user.username}}

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(lambda: SessionLocal())):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username, "role": user.role.value},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "lab_name": user.lab_name,
            "role": user.role.value
        }
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "id": current_user["user_id"],
        "username": current_user["username"],
        "role": current_user["role"]
    }

@router.get("/list", response_model=list[UserResponse])
def get_user_list(current_user: dict = Depends(get_admin_user), db: Session = Depends(lambda: SessionLocal())):
    """获取用户列表（管理员权限）"""
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "full_name": u.full_name, "lab_name": u.lab_name, "role": u.role.value} for u in users]

@router.put("/password", response_model=dict)
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(lambda: SessionLocal())
):
    """修改当前用户密码"""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not verify_password(request.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    user.password_hash = get_password_hash(request.new_password)
    db.commit()
    return {"msg": "密码修改成功"}

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, current_user: dict = Depends(get_admin_user), db: Session = Depends(lambda: SessionLocal())):
    """删除用户（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return {"msg": "删除成功"}
