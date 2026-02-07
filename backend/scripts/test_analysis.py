"""测试 AI 分析功能"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import AsyncSessionLocal
from app.models.models import Case
from app.services.legal_agent import LegalAnalysisAgent
from sqlalchemy import select


async def test_analysis():
    """测试案件分析"""
    async with AsyncSessionLocal() as db:
        # 获取第一个案件
        result = await db.execute(select(Case).limit(1))
        case = result.scalar_one_or_none()

        if not case:
            print("没有找到案件")
            return

        print(f"测试案件: {case.title}")
        print(f"案件ID: {case.id}")
        print("-" * 50)

        try:
            # 创建 Agent
            agent = LegalAnalysisAgent(db)

            # 执行分析
            result = await agent.analyze_case(case.content)

            print("\n分析结果:")
            print(f"摘要: {result.get('summary', 'N/A')}")
            print(f"关键要素: {result.get('key_elements', {})}")
            print(f"法律依据: {result.get('legal_basis', [])}")

        except Exception as e:
            print(f"\n错误: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_analysis())
