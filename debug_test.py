import asyncio
import sys
sys.path.append('.')

from gal_sim.services.llm_service import LLMService

def test_service():
    service = LLMService()
    try:
        print('测试生成主题...')
        theme = service.generate_theme()
        print(f'主题生成成功: {theme}')
        
        print('测试生成初始对话...')
        dialogue = service.generate_initial_dialogue(theme)
        print(f'对话生成成功，选项数: {len(dialogue["choices"])}')
        
        print('测试完成')
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()