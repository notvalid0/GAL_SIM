from typing import Dict, Any, List
from .llm_service import LLMService
from .session_manager import session_manager, SessionData
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

logger = logging.getLogger(__name__)


class DialogueService:
    def __init__(self):
        self.llm_service = LLMService()
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def start_new_dialogue(self, session_id: str, theme: str = None, custom_theme: str = None) -> Dict[str, Any]:
        """开始新的对话"""
        try:
            # 确定主题
            if custom_theme:
                final_theme = custom_theme
            elif theme == "auto" or not theme:
                final_theme = self.llm_service.generate_theme()
            else:
                final_theme = theme
            
            # 生成初始对话
            dialogue_data = self.llm_service.generate_initial_dialogue(final_theme)
            
            # 创建会话
            session_data = await session_manager.create_session(session_id, final_theme)
            
            # 添加初始对话到历史记录
            session_data.add_message("character", dialogue_data["dialogue"])
            
            logger.info(f"Started new dialogue session: {session_id} with theme: {final_theme}")
            
            return {
                "theme": final_theme,
                "initial_dialogue": dialogue_data["dialogue"],
                "choices": dialogue_data["choices"],
                "affection": session_data.affection
            }
        except Exception as e:
            logger.error(f"Error starting dialogue: {str(e)}")
            raise

    async def continue_dialogue(self, session_id: str, user_input: str, theme: str = None) -> Dict[str, Any]:
        """继续对话"""
        try:
            # 获取会话
            session_data = await session_manager.get_session(session_id)
            if not session_data:
                raise ValueError(f"Session {session_id} not found or expired")
            
            # 如果提供了新的主题，更新会话
            if theme and session_data.theme != theme:
                session_data.theme = theme
            
            # 计算好感度变化
            affection_change = self._calculate_affection_change(user_input)
            session_data.update_affection(affection_change)
            
            # 添加用户输入到历史记录
            session_data.add_message("user", user_input)
            
            # 获取AI回应
            response_data = self.llm_service.generate_response(
                session_data.theme,
                session_data.history,
                user_input
            )
            
            # 添加AI回应到历史记录
            session_data.add_message("character", response_data["response"])
            
            logger.info(f"Continued dialogue for session: {session_id}")
            
            return {
                "character_response": response_data["response"],
                "choices": response_data["choices"],
                "affection": session_data.affection
            }
        except Exception as e:
            logger.error(f"Error continuing dialogue: {str(e)}")
            raise

    def _calculate_affection_change(self, user_choice: str) -> int:
        """根据用户选择计算好感度变化"""
        # 检查选项文本中是否包含好感度变化的标记
        if "A" in user_choice or "好感度 +3" in user_choice:
            return 3
        elif "B" in user_choice or "好感度 +1" in user_choice:
            return 1
        elif "C" in user_choice or "好感度 -1" in user_choice:
            return -1
        elif "D" in user_choice or "好感度 -3" in user_choice:
            return -3
        else:
            # 如果没有明确标记，尝试通过关键词判断
            lower_choice = user_choice.lower()
            if any(keyword in lower_choice for keyword in ["亲密", "拥抱", "喜欢", "爱", "支持", "温柔", "关心", "理解"]):
                return 1
            elif any(keyword in lower_choice for keyword in ["冷漠", "忽视", "忽视", "离开", "忽视", "生气", "愤怒", "讨厌"]):
                return -1
            else:
                return 0  # 无变化

    async def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """获取会话数据"""
        try:
            session_data = await session_manager.get_session(session_id)
            if not session_data:
                return None
            
            return {
                "session_id": session_data.session_id,
                "theme": session_data.theme,
                "history_length": len(session_data.history),
                "created_at": session_data.created_at.isoformat(),
                "last_accessed": session_data.last_accessed.isoformat(),
                "affection": session_data.affection
            }
        except Exception as e:
            logger.error(f"Error getting session data: {str(e)}")
            raise