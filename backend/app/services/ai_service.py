from anthropic import AsyncAnthropic
from app.core.config import settings

# 创建客户端，支持自定义 base_url
client_kwargs = {"api_key": settings.ANTHROPIC_API_KEY}
if settings.ANTHROPIC_BASE_URL:
    client_kwargs["base_url"] = settings.ANTHROPIC_BASE_URL

client = AsyncAnthropic(**client_kwargs)


async def analyze_case(case_content: str) -> dict:
    """使用 Claude 分析案例"""

    prompt = f"""你是一位资深法律专家。请分析以下判决书：

{case_content}

请提供：
1. 案情摘要（200字以内）
2. 关键要素：
   - 当事人信息
   - 案由
   - 争议焦点
3. 判决理由分析
4. 法律依据
5. 裁判结果及其合理性

请用专业但易懂的语言回答，以 JSON 格式返回，格式如下：
{{
  "summary": "案情摘要",
  "key_elements": {{
    "parties": "当事人信息",
    "case_cause": "案由",
    "dispute_focus": "争议焦点"
  }},
  "legal_reasoning": "判决理由分析",
  "legal_basis": ["法律依据1", "法律依据2"],
  "judgment_result": "裁判结果"
}}
"""

    message = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=32000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # 提取响应内容
    response_text = message.content[0].text

    # 尝试解析 JSON
    import json
    try:
        # 提取 JSON 部分（可能包含在代码块中）
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text

        result = json.loads(json_str)
        return result
    except Exception as e:
        # 如果解析失败，返回原始文本
        return {
            "summary": response_text[:200],
            "key_elements": {},
            "legal_reasoning": response_text,
            "legal_basis": [],
            "judgment_result": ""
        }
