"""直接测试 AI 是否生成通俗版"""
import asyncio
from app.db.database import AsyncSessionLocal
from app.models.models import Case
from app.services.legal_agent import LegalAnalysisAgent
from sqlalchemy import select


async def test():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Case).where(Case.id == 5))
        case = result.scalar_one_or_none()

        print(f"测试案件: {case.title}")
        print("=" * 60)

        agent = LegalAnalysisAgent(db)
        analysis = await agent.analyze_case(case.content)

        print("\n【专业版摘要】")
        print(analysis.get('summary', 'N/A')[:200])

        print("\n【通俗版摘要】")
        print(analysis.get('summary_plain', 'N/A')[:200])

        print("\n【是否相同？】")
        if analysis.get('summary') == analysis.get('summary_plain'):
            print("❌ 相同！AI 没有生成不同的版本")
        else:
            print("✅ 不同！AI 正确生成了两个版本")


if __name__ == "__main__":
    asyncio.run(test())
