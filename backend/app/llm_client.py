import requests
import json
import traceback
from .config import API_BASE_URL, API_KEY

class ApiClient:
    def __init__(self):
        print("使用 API 调用模式")
        self.api_base_url = API_BASE_URL
        self.api_key = API_KEY
        print(f"API基础URL: {self.api_base_url}")
        print(f"API密钥状态: {'已配置' if self.api_key else '未配置'}")
        
        # 检测API提供商
        if "dashscope" in self.api_base_url:
            self.provider = "aliyun"
        elif "siliconflow" in self.api_base_url:
            self.provider = "siliconflow"
        elif "openai" in self.api_base_url.lower():
            self.provider = "openai"
        else:
            self.provider = "default"
        print(f"API提供商: {self.provider}")

    def generate(self, prompt: str, max_new_tokens=512):
        headers = {
            "Content-Type": "application/json",
        }
        
        # 根据提供商设置不同的授权方式
        if self.provider == "aliyun":
            headers["Authorization"] = f"Bearer {self.api_key}"
            model_name = "qwen3.6-plus"
        elif self.provider == "siliconflow":
            headers["Authorization"] = f"Bearer {self.api_key}"
            model_name = "Qwen/Qwen3-8B"
            print(f"使用 SiliconFlow 模型: {model_name}")
        elif self.provider == "openai":
            headers["Authorization"] = f"Bearer {self.api_key}"
            model_name = "gpt-4o-mini"
        else:
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            model_name = "Qwen/Qwen2-7B-Instruct"

        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }

        try:
            print(f"正在调用API: {self.api_base_url}/chat/completions")
            print(f"请求数据: {json.dumps(data, ensure_ascii=False)[:200]}...")
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=120
            )
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
            
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e}")
            print(f"响应内容: {response.text if 'response' in dir() else 'N/A'}")
            return f"API调用失败: HTTP {response.status_code} - {response.text[:200]}"
        except Exception as e:
            print(f"API调用失败: {type(e).__name__}: {e}")
            traceback.print_exc()
            return "抱歉，当前服务暂时不可用，请稍后重试。"

# 全局实例
llm = ApiClient()