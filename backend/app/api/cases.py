from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from app.db.database import get_db
from app.models.models import Case, User, SearchHistory
from app.schemas.schemas import (
    CaseCreate, CaseResponse, SearchRequest, SearchResponse,
    AnalysisRequest, AnalysisResponse
)
from app.api.auth import get_current_user
from app.services.ai_service import analyze_case
from app.services.legal_agent import LegalAnalysisAgent

router = APIRouter(prefix="/cases", tags=["案例"])


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建案例（管理员功能）"""
    # 检查案例编号是否存在
    result = await db.execute(select(Case).where(Case.case_number == case_data.case_number))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="案例编号已存在")

    case = Case(**case_data.model_dump())
    db.add(case)
    await db.commit()
    await db.refresh(case)

    return case


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取案例详情"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    return case


@router.post("/search", response_model=SearchResponse)
async def search_cases(
    search_req: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """搜索案例"""
    query = search_req.query
    page = search_req.page
    page_size = search_req.page_size
    filters = search_req.filters or {}

    # 构建查询
    stmt = select(Case)

    # 关键词搜索（标题或内容）
    if query:
        stmt = stmt.where(
            or_(
                Case.title.ilike(f"%{query}%"),
                Case.content.ilike(f"%{query}%")
            )
        )

    # 应用过滤器
    if filters.get("case_type"):
        stmt = stmt.where(Case.case_type == filters["case_type"])

    if filters.get("court"):
        stmt = stmt.where(Case.court.ilike(f"%{filters['court']}%"))

    # 计算总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    # 分页
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # 执行查询
    result = await db.execute(stmt)
    cases = result.scalars().all()

    # 保存搜索历史
    search_history = SearchHistory(
        user_id=current_user.id,
        query=query,
        filters=filters,
        results_count=total
    )
    db.add(search_history)
    await db.commit()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": cases
    }


@router.post("/{case_id}/analyze", response_model=AnalysisResponse)
async def analyze_case_endpoint(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """分析案例 - 使用 Agent 进行智能分析

    这不是简单的提示词调用，而是一个真正的 Agent：
    1. 自动提取案例要素
    2. 主动搜索相似案例
    3. 查找相关法律依据
    4. 综合所有信息进行深度分析
    """
    # 获取案例
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 使用 Legal Analysis Agent 进行分析
    try:
        # 创建 Agent 实例
        agent = LegalAnalysisAgent(db)

        # Agent 自主执行多步骤分析
        analysis = await agent.analyze_case(case.content)

        return {
            "case_id": case_id,
            "summary": analysis.get("summary", ""),
            "summary_plain": analysis.get("summary_plain"),
            "key_elements": analysis.get("key_elements", {}),
            "key_elements_plain": analysis.get("key_elements_plain"),
            "legal_reasoning": analysis.get("legal_reasoning", ""),
            "legal_reasoning_plain": analysis.get("legal_reasoning_plain"),
            "legal_basis": analysis.get("legal_basis", []),
            "legal_basis_plain": analysis.get("legal_basis_plain"),
            "judgment_result": analysis.get("judgment_result", ""),
            "judgment_result_plain": analysis.get("judgment_result_plain"),
            "plain_language_tips": analysis.get("plain_language_tips")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 分析失败: {str(e)}")
