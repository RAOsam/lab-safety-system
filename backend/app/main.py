from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import qa, user, image_inspect, inspection

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="实验室安全智能问答系统")

# CORS 配置，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(qa.router)
app.include_router(user.router)
app.include_router(image_inspect.router)
app.include_router(inspection.router)

@app.get("/")
def root():
    return {"message": "实验室安全问答系统API运行中"}