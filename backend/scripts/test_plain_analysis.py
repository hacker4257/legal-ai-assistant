"""测试 AI 分析返回的字段"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import AsyncSessionLocal
from app.models.models import Case
from app.services.legal_agent import LegalAnalysisAgent
from sqlalchemy import select


async def test_analysis():
    """测试案件分析"""
    async with AsyncSessionLocal() as db:
        # 获取第二个案件
        result = await db.execute(select(Case).where(Case.id == 2))
        case = result.scalar_one_or_none()

        if not case:
            print("没有找到案件")
            return

        print(f"测试案件: {case.title}")
        print("-" * 50)

        try:
            # 创建 Agent
            agent = LegalAnalysisAgent(db)

            # 执行分析
            result = await agent.analyze_case(case.content)

            print("\n返回的字段:")
            for key in result.keys():
                print(f"  - {key}")

            print("\n是否有通俗版字段:")
            print(f"  summary_plain: {'summary_plain' in result}")
            print(f"  key_elements_plain: {'key_elements_plain' in result}")
            print(f"  legal_reasoning_plain: {'legal_reasoning_plain' in result}")

            if 'summary_plain' in result:
                print(f"\n通俗版摘要: {result['summary_plain'][:100]}...")
            else:
                print("\n⚠️ 缺少通俗版字段！")

        except Exception as e:
            print(f"\n错误: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_analysis())
