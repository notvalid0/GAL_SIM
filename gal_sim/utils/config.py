import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

# 验证必要的环境变量
if not LLM_API_KEY:
    raise ValueError("LLM_API_KEY 环境变量未设置，请在 .env 文件中配置")