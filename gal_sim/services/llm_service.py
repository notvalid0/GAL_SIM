from openai import OpenAI
from typing import List, Dict, Any
from ..utils.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from ..utils.dialogue_utils import validate_choices, sanitize_text, ensure_json_format


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=LLM_API_KEY)
        if LLM_BASE_URL:
            self.client.base_url = LLM_BASE_URL

    def generate_theme(self) -> str:
        """生成对话主题"""
        prompt = """请生成一个适合Galgame对话的有趣主题。主题应该包含场景和人物关系的简要描述。
        例如：'校园恋爱'、'魔法学院的邂逅'、'未来世界的机器人伙伴'等。
        只返回主题名称，不要其他内容。"""
        
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            # 直接获取内容并转换为字符串
            content = response.choices[0].message.content
            if content is None:
                raise Exception("API返回内容为空")
            return str(content).strip()
        except Exception as e:
            raise Exception(f"生成主题失败: {str(e)}")

    def generate_initial_dialogue(self, theme: str) -> Dict[str, Any]:
        """根据主题生成初始对话和选项"""
        prompt = f"""你是Galgame中的角色，现在开始一个关于"{theme}"的对话。
        请生成一段吸引人的开场白，然后提供四个不同的选择（A、B、C、D）供用户选择。
        每个选项对好感度的影响：
        - 选项A: 好感度+3（非常符合角色喜好）
        - 选项B: 好感度+1（比较符合角色喜好）
        - 选项C: 好感度-1（可能让角色不开心）
        - 选项D: 好感度-3（严重冒犯角色）
        
        请按照以下JSON格式返回：
        {{
          "dialogue": "角色的开场白",
          "choices": [
            "选项A的内容",
            "选项B的内容",
            "选项C的内容",
            "选项D的内容"
          ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # 处理响应，确保格式正确
            raw_response = response.choices[0].message.content
            if raw_response is None:
                raise Exception("API返回内容为空")
            raw_response = str(raw_response).strip()
            
            result = ensure_json_format(raw_response)
            
            dialogue = sanitize_text(result.get("dialogue", ""))
            choices = validate_choices(result.get("choices", ["", "", "", ""]))
            
            return {
                "dialogue": dialogue,
                "choices": choices
            }
        except Exception as e:
            raise Exception(f"生成初始对话失败: {str(e)}")

    def generate_response(self, theme: str, history: List[Dict], user_choice: str) -> Dict[str, Any]:
        """根据用户选择生成角色回应和新选项"""
        from ..utils.dialogue_utils import format_dialogue_history
        history_text = format_dialogue_history(history)
        
        prompt = f"""你是一个Galgame中的角色，当前故事主题是"{theme}"。
        对话历史：
        {history_text}
        
        用户选择了：{user_choice}
        
        请回应用户的选择，并提供四个新的选择（A、B、C、D）让用户继续剧情。
        每个选项对好感度的影响：
        - 选项A: 好感度+3（非常符合角色喜好）
        - 选项B: 好感度+1（比较符合角色喜好）
        - 选项C: 好感度-1（可能让角色不开心）
        - 选项D: 好感度-3（严重冒犯角色）
        
        请按照以下JSON格式返回：
        {{
          "response": "角色对用户选择的回应",
          "choices": [
            "选项A的内容",
            "选项B的内容", 
            "选项C的内容",
            "选项D的内容"
          ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # 处理响应，确保格式正确
            raw_response = response.choices[0].message.content
            if raw_response is None:
                raise Exception("API返回内容为空")
            raw_response = str(raw_response).strip()
            
            result = ensure_json_format(raw_response)
            
            response_text = sanitize_text(result.get("response", ""))
            choices = validate_choices(result.get("choices", ["", "", "", ""]))
            
            return {
                "response": response_text,
                "choices": choices
            }
        except Exception as e:
            raise Exception(f"生成对话回应失败: {str(e)}")