from fastapi import APIRouter, HTTPException
from ..models.dialogue import DialogueRequest, DialogueResponse, ThemeRequest, ThemeResponse
from ..services.dialogue_service import DialogueService
from typing import Dict
import uuid

router = APIRouter(prefix="/api/v1", tags=["dialogue"])

# 对话服务实例
dialogue_service = DialogueService()


@router.post("/start", response_model=ThemeResponse)
async def start_dialogue(request: ThemeRequest):
    """
    开始新的对话
    - 如果theme为空，则自动生成主题
    - 返回初始对话和四个选项
    """
    try:
        session_id = str(uuid.uuid4())
        result = await dialogue_service.start_new_dialogue(session_id, request.theme, request.custom_theme)
        return ThemeResponse(
            session_id=session_id,
            theme=result["theme"],
            initial_dialogue=result["initial_dialogue"],
            choices=result["choices"],
            affection=result["affection"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始对话失败: {str(e)}")


@router.post("/dialogue", response_model=DialogueResponse)
async def continue_dialogue(request: DialogueRequest):
    """
    继续对话
    - 根据用户的选择继续剧情
    - 返回角色回应和新的四个选项
    """
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="会话ID不能为空")
        
        result = await dialogue_service.continue_dialogue(request.session_id, request.user_input, request.theme)
        return DialogueResponse(
            session_id=request.session_id,
            character_response=result["character_response"],
            choices=result["choices"],
            affection=result["affection"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话继续失败: {str(e)}")


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    获取会话信息
    """
    try:
        session_data = await dialogue_service.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="会话不存在")
        return session_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话信息失败: {str(e)}")