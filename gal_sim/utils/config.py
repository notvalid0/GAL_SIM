import os
from dotenv import load_dotenv

# 尝试加载环境变量，优先级：当前目录 -> 父目录 -> 应用根目录
def load_env_vars():
    """尝试从多个可能的位置加载环境变量"""
    possible_paths = [
        '.env',  # 当前目录
        '../.env',  # 父目录
        '../../.env',  # 上两级目录
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),  # 项目根目录
    ]
    
    for env_path in possible_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            return True
    
    # 如果都找不到，尝试加载默认的环境变量
    load_dotenv()  # 尝试加载当前工作目录下的 .env
    return False

# 加载环境变量
load_env_vars()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

# 验证必要的环境变量
if not LLM_API_KEY or LLM_API_KEY == "your_api_key_here":
    print("⚠️  警告: LLM_API_KEY 未设置或仍为默认值，请在 .env 文件中配置")
    print("   示例: LLM_API_KEY=sk-...")
    LLM_API_KEY = ""  # 确保变量存在但为空字符串