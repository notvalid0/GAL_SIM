"""
简单的测试脚本，验证GAL-SIM应用的基本功能
"""
import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from gal_sim.services.llm_service import LLMService
from gal_sim.services.session_manager import session_manager
from gal_sim.utils.config import LLM_API_KEY

async def test_llm_connection():
    """测试LLM连接"""
    print("测试LLM连接...")
    if not LLM_API_KEY:
        print("❌ LLM_API_KEY 未设置，请检查 .env 文件")
        return False
    
    llm_service = LLMService()
    
    try:
        theme = await llm_service.generate_theme()
        print(f"✅ 主题生成成功: {theme}")
        
        initial_dialogue = await llm_service.generate_initial_dialogue(theme)
        print(f"✅ 初始对话生成成功")
        print(f"   对话: {initial_dialogue['dialogue'][:50]}...")
        print(f"   选项数量: {len(initial_dialogue['choices'])}")
        
        return True
    except Exception as e:
        print(f"❌ LLM连接测试失败: {e}")
        return False

async def test_session_management():
    """测试会话管理"""
    print("\n测试会话管理...")
    
    try:
        session_id = "test_session_123"
        theme = "测试主题"
        
        # 创建会话
        session_data = await session_manager.create_session(session_id, theme)
        print(f"✅ 会话创建成功: {session_data.session_id}")
        
        # 添加消息
        session_data.add_message("user", "你好")
        session_data.add_message("character", "你好呀！")
        print(f"✅ 消息添加成功，历史记录数量: {len(session_data.history)}")
        
        # 获取会话
        retrieved_session = await session_manager.get_session(session_id)
        if retrieved_session:
            print(f"✅ 会话检索成功: {retrieved_session.session_id}")
        else:
            print("❌ 会话检索失败")
            return False
        
        # 删除会话
        await session_manager.delete_session(session_id)
        print("✅ 会话删除成功")
        
        return True
    except Exception as e:
        print(f"❌ 会话管理测试失败: {e}")
        return False

async def main():
    print("开始测试GAL-SIM应用...")
    
    # 测试LLM连接
    llm_ok = await test_llm_connection()
    
    # 测试会话管理
    session_ok = await test_session_management()
    
    print(f"\n测试结果:")
    print(f"LLM连接: {'✅ 通过' if llm_ok else '❌ 失败'}")
    print(f"会话管理: {'✅ 通过' if session_ok else '❌ 失败'}")
    
    if llm_ok and session_ok:
        print("\n🎉 所有测试通过！应用已准备就绪。")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查配置。")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)