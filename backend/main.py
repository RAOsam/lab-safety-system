"""
实验室安全问答系统 - 入口文件
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动应用"""
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()