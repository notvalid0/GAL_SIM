import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class SessionData:
    """会话数据类"""
    session_id: str
    theme: str
    history: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    max_history_length: int = 50  # 最大历史记录数
    affection: int = 50  # 好感度，初始值为50
    
    def add_message(self, role: str, content: str):
        """添加消息到历史记录"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]
        
        self.last_accessed = datetime.now()
    
    def update_affection(self, change: int):
        """更新好感度"""
        self.affection += change
        # 限制好感度在0-100范围内
        self.affection = max(0, min(100, self.affection))


class SessionManager:
    """会话管理器"""
    def __init__(self, session_timeout: int = 3600):  # 1小时超时
        self.sessions: Dict[str, SessionData] = {}
        self.session_timeout = session_timeout
        self.lock = asyncio.Lock()
    
    async def create_session(self, session_id: str, theme: str) -> SessionData:
        """创建新会话"""
        async with self.lock:
            session_data = SessionData(session_id=session_id, theme=theme)
            self.sessions[session_id] = session_data
            return session_data
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """获取会话"""
        async with self.lock:
            session_data = self.sessions.get(session_id)
            if session_data:
                # 检查会话是否超时
                time_since_access = datetime.now() - session_data.last_accessed
                if time_since_access.total_seconds() > self.session_timeout:
                    await self.delete_session(session_id)
                    return None
                return session_data
            return None
    
    async def update_session(self, session_id: str, **kwargs) -> bool:
        """更新会话数据"""
        async with self.lock:
            session_data = self.sessions.get(session_id)
            if session_data:
                for key, value in kwargs.items():
                    if hasattr(session_data, key):
                        setattr(session_data, key, value)
                session_data.last_accessed = datetime.now()
                return True
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        async with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False
    
    async def cleanup_expired_sessions(self):
        """清理过期会话"""
        async with self.lock:
            expired_sessions = []
            current_time = datetime.now()
            
            for session_id, session_data in self.sessions.items():
                time_since_access = current_time - session_data.last_accessed
                if time_since_access.total_seconds() > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                
            return len(expired_sessions)


# 全局会话管理器实例
session_manager = SessionManager()