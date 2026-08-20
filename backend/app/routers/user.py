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
    full_name: str | None = None
    lab_name: str | None = None
    role: str | None = None

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
        role=UserRole.USER.value
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
        data={"sub": user.id, "username": user.username, "role": user.role},
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
            "role": user.role
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
    return [{"id": u.id, "username": u.username, "full_name": u.full_name, "lab_name": u.lab_name, "role": u.role} for u in users]

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

# ===== 前端兼容路由（匹配 UserManage.vue 的调用方式） =====
# 前端调用: GET /api/users, POST /api/users, PUT /api/users/:id, DELETE /api/users/:id
# 前端字段: username, password, email, phone, department, role

from typing import Optional

frontend_router = APIRouter(prefix="/api", tags=["用户管理(前端兼容)"])

class FrontendUserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = "user"

class FrontendUserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None

@frontend_router.get("/users")
def frontend_user_list(current_user: dict = Depends(get_admin_user), db: Session = Depends(lambda: SessionLocal())):
    """获取用户列表（管理员权限）"""
    users = db.query(User).all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "lab_name": u.lab_name,
            "email": u.email,
            "phone": u.phone,
            "department": u.lab_name,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    return result

@frontend_router.post("/users")
def frontend_create_user(user: FrontendUserCreate, current_user: dict = Depends(get_admin_user), db: Session = Depends(lambda: SessionLocal())):
    """创建用户（管理员权限）"""
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    new_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        full_name=user.username,
        lab_name=user.department,
        phone=user.phone,
        email=user.email,
        role=user.role if user.role in ["admin", "user"] else "user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "full_name": new_user.full_name,
        "lab_name": new_user.lab_name,
        "email": new_user.email,
        "phone": new_user.phone,
        "department": new_user.lab_name,
        "role": new_user.role,
        "created_at": new_user.created_at.isoformat() if new_user.created_at else None
    }

@frontend_router.put("/users/{user_id}")
def frontend_update_user(user_id: int, update: FrontendUserUpdate, current_user: dict = Depends(get_admin_user), db: Session = Depends(lambda: SessionLocal())):
    """更新用户（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if update.email is not None:
        user.email = update.email
    if update.phone is not None:
        user.phone = update.phone
    if update.department is not None:
        user.lab_name = update.department
    if update.role is not None:
        user.role = update.role if update.role in ["admin", "user"] else user.role
    
    db.commit()
    db.refresh(user)
    return {"msg": "更新成功"}

@frontend_router.delete("/users/{user_id}")
def frontend_delete_user(user_id: int, current_user: dict = Depends(get_admin_user), db: Session = Depends(lambda: SessionLocal())):
    """删除用户（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return {"msg": "删除成功"}
