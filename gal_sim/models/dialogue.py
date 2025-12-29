from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from enum import Enum


class DialogueRequest(BaseModel):
    """对话请求模型"""
    user_input: str
    session_id: Optional[str] = None
    theme: Optional[str] = None


class DialogueResponse(BaseModel):
    """对话响应模型"""
    session_id: str
    character_response: str
    choices: List[str]  # A, B, C, D 四个选项
    timestamp: datetime = datetime.now()
    affection: int  # 好感度


class ThemeRequest(BaseModel):
    """主题请求模型"""
    theme: Optional[str] = None  # 如果为空则自动生成主题
    custom_theme: Optional[str] = None  # 用户自定义主题


class ThemeResponse(BaseModel):
    """主题响应模型"""
    session_id: str
    theme: str
    initial_dialogue: str
    choices: List[str]  # A, B, C, D 四个选项
    timestamp: datetime = datetime.now()
    affection: int = 50  # 初始好感度为50


class ChoiceType(Enum):
    """选项类型枚举"""
    PLUS_3 = "PLUS_3"  # 好感度+3
    PLUS_1 = "PLUS_1"  # 好感度+1
    MINUS_1 = "MINUS_1"  # 好感度-1
    MINUS_3 = "MINUS_3"  # 好感度-3