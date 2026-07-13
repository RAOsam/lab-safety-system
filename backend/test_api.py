from app.routers.qa import ask
from app.database import SessionLocal
from pydantic import BaseModel

class Question(BaseModel):
    user_id: int = None
    question: str = "测试"

def test_ask():
    try:
        db = SessionLocal()
        question = Question()
        print(f"测试问题: {question.question}")
        print(f"测试用户ID: {question.user_id}")
        result = ask(question, db)
        print(f"结果: {result}")
        db.close()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ask()