"""
GAL-SIM 启动脚本
"""
import uvicorn
import os
import sys
from gal_sim.utils.config import *

def main():
    print("启动 GAL-SIM - Galgame对话模拟器...")
    
    # 检查环境变量
    try:
        from gal_sim.utils.config import LLM_API_KEY
        if not LLM_API_KEY or LLM_API_KEY == "your_api_key_here":
            print("⚠️  警告: LLM_API_KEY 未设置或仍为默认值，请在 .env 文件中配置")
            print("   示例: LLM_API_KEY=sk-...")
    except Exception as e:
        print(f"⚠️  警告: 无法加载配置 - {e}")
    
    print("服务器将在 http://127.0.0.1:8000 上启动")
    print("按 Ctrl+C 停止服务器")
    
    try:
        uvicorn.run(
            "gal_sim.main:app",
            host="127.0.0.1",  # 使用127.0.0.1而不是0.0.0.0以提高安全性
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        print("请检查以下问题：")
        print("1. 端口8000是否被占用")
        print("2. Python依赖是否已正确安装")
        print("3. .env配置文件是否正确")
        input("按回车键退出...")

if __name__ == "__main__":
    main()