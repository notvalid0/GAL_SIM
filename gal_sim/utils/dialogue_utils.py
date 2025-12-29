from typing import List, Dict, Any
import re


def validate_choices(choices: List[str]) -> List[str]:
    """
    验证并清理选项，确保有4个有效选项
    """
    # 确保我们有4个选项
    if len(choices) < 4:
        # 补充空选项
        choices.extend([""] * (4 - len(choices)))
    elif len(choices) > 4:
        # 只取前4个
        choices = choices[:4]
    
    # 清理选项内容，去除多余空白
    cleaned_choices = []
    for choice in choices:
        if choice is None:
            choice = ""
        cleaned_choice = re.sub(r'\s+', ' ', str(choice).strip())
        cleaned_choices.append(cleaned_choice)
    
    return cleaned_choices


def format_dialogue_history(history: List[Dict[str, str]], max_entries: int = 10) -> str:
    """
    格式化对话历史，用于提供给LLM上下文
    """
    # 只取最近的对话条目
    recent_history = history[-max_entries:] if len(history) > max_entries else history
    
    formatted_history = []
    for entry in recent_history:
        role = "用户" if entry["role"] == "user" else "角色"
        content = entry["content"]
        formatted_history.append(f"{role}: {content}")
    
    return "\n".join(formatted_history)


def sanitize_text(text: str) -> str:
    """
    清理文本，移除不安全或不需要的内容
    """
    # 移除多余的换行符和空格
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # 过滤可能的恶意内容（简单示例）
    # 在实际应用中可以加入更复杂的过滤逻辑
    
    return text


def extract_choices_from_text(text: str) -> List[str]:
    """
    从文本中提取选项（如果LLM没有按JSON格式返回）
    """
    # 查找A、B、C、D选项的模式
    patterns = [
        r'[A-D]\.\s*(.*?)(?=\n[A-D]\.|$)',
        r'选项[A-D]：(.*?)(?=选项[A-D]|$)',
        r'选项[A-D]\s*[:：]\s*(.*?)(?=选项[A-D]|$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        if len(matches) >= 4:
            choices = [match.strip() for match in matches[:4]]
            if all(choices):  # 确保所有选项都有内容
                return choices
    
    # 如果找不到标准格式，尝试按行分割并查找选项
    lines = text.split('\n')
    choices = []
    for line in lines:
        line = line.strip()
        if line.startswith(('A.', 'B.', 'C.', 'D.')):
            content = line[2:].strip()
            if content:
                choices.append(content)
        elif line.startswith(('A：', 'B：', 'C：', 'D：')):
            content = line[2:].strip()
            if content:
                choices.append(content)
        elif line.startswith(('A:', 'B:', 'C:', 'D:')):
            content = line[2:].strip()
            if content:
                choices.append(content)
    
    if len(choices) >= 4:
        return choices[:4]
    
    # 如果仍然找不到4个选项，返回空列表
    return ["", "", "", ""]


def ensure_json_format(response: str) -> Dict[str, Any]:
    """
    尝试将响应转换为JSON格式
    """
    import json
    import re
    
    # 尝试直接解析JSON
    try:
        return json.loads(response)
    except:
        pass
    
    # 查找JSON对象
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group()
            return json.loads(json_str)
        except:
            pass
    
    # 如果没有JSON格式，尝试从文本中提取信息
    result = {"response": response, "choices": ["", "", "", ""]}
    
    # 尝试提取选项
    choices = extract_choices_from_text(response)
    if choices and any(choices):
        result["choices"] = choices
    
    # 尝试分离响应和选项
    lines = response.split('\n')
    non_choice_lines = []
    for line in lines:
        if not (line.strip().startswith(('A.', 'B.', 'C.', 'D.', 'A：', 'B：', 'C：', 'D：', 'A:', 'B:', 'C:', 'D:'))):
            non_choice_lines.append(line)
    
    result["response"] = "\n".join(non_choice_lines).strip()
    
    return result