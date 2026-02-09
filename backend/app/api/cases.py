from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
import shutil
from pathlib import Path
import uuid
from io import BytesIO

from app.db.database import get_db
from app.models.models import Case, User, SearchHistory, CaseAnalysis
from app.schemas.schemas import (
    CaseCreate, CaseResponse, SearchRequest, SearchResponse,
    AnalysisRequest, AnalysisResponse
)
from app.api.auth import get_current_user
from app.services.ai_service import analyze_case
from app.services.legal_agent import LegalAnalysisAgent
from app.services.pdf_service import PDFService
from app.services.pdf_export_service import PDFExportService
from app.services.vector_service import vector_service

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

    # 异步存储到向量数据库
    try:
        await vector_service.upsert_case(
            case_id=case.id,
            title=case.title,
            content=case.content or "",
            case_type=case.case_type,
            court=case.court,
            case_number=case.case_number
        )
    except Exception as e:
        # 向量存储失败不影响主流程
        import logging
        logging.warning(f"Failed to store case vector: {e}")

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
    """搜索案例

    支持两种搜索模式：
    1. 混合搜索（语义 + 关键词）- 需要 Qdrant 服务
    2. 关键词搜索 - 回退方案

    混合搜索更智能，能找到语义相关的案例
    """
    query = search_req.query
    page = search_req.page
    page_size = search_req.page_size
    filters = search_req.filters or {}

    # 尝试使用向量搜索
    use_vector_search = query and await vector_service.is_available()

    if use_vector_search:
        try:
            # 使用混合搜索
            vector_results = await vector_service.hybrid_search(
                query=query,
                top_k=page_size * 2,  # 获取更多结果用于过滤
                filters=filters,
                semantic_weight=0.7
            )

            # 获取案例 ID 列表
            case_ids = [r["id"] for r in vector_results]

            if case_ids:
                # 从数据库获取完整案例信息
                stmt = select(Case).where(Case.id.in_(case_ids))
                result = await db.execute(stmt)
                cases_map = {case.id: case for case in result.scalars().all()}

                # 按向量搜索分数排序
                cases = []
                for r in vector_results:
                    if r["id"] in cases_map:
                        cases.append(cases_map[r["id"]])

                # 分页
                total = len(cases)
                start = (page - 1) * page_size
                end = start + page_size
                cases = cases[start:end]
            else:
                cases = []
                total = 0

        except Exception as e:
            # 向量搜索失败，回退到关键词搜索
            import logging
            logging.warning(f"Vector search failed, falling back to keyword search: {e}")
            use_vector_search = False

    if not use_vector_search:
        # 关键词搜索（回退方案）
        stmt = select(Case)

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

    ✨ 分析结果会被缓存，避免重复调用 AI API
    """
    # 获取案例
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查是否有缓存的分析结果
    cache_result = await db.execute(
        select(CaseAnalysis).where(CaseAnalysis.case_id == case_id)
    )
    cached_analysis = cache_result.scalar_one_or_none()

    if cached_analysis:
        # 返回缓存的结果
        analysis_data = cached_analysis.analysis_result
        return {
            "case_id": case_id,
            **analysis_data
        }

    # 没有缓存，使用 Legal Analysis Agent 进行分析
    try:
        # 创建 Agent 实例
        agent = LegalAnalysisAgent(db)

        # Agent 自主执行多步骤分析
        analysis = await agent.analyze_case(case.content)

        # 准备返回数据
        response_data = {
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

        # 保存到缓存
        cache_entry = CaseAnalysis(
            case_id=case_id,
            analysis_result=response_data
        )
        db.add(cache_entry)
        await db.commit()

        return {
            "case_id": case_id,
            **response_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 分析失败: {str(e)}")


@router.post("/upload", response_model=CaseResponse, status_code=201)
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传 PDF 法律文书

    支持：
    - PDF 格式
    - 最大 10MB
    - 自动提取文本和案件信息
    """
    # 验证文件类型
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持 PDF 格式")

    # 创建上传目录
    upload_dir = Path("/app/uploads")
    upload_dir.mkdir(exist_ok=True)

    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}.pdf"

    try:
        # 保存文件
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 验证 PDF
        is_valid, error_msg = PDFService.validate_pdf(str(file_path))
        if not is_valid:
            file_path.unlink()  # 删除无效文件
            raise HTTPException(status_code=400, detail=error_msg)

        # 提取文本
        text = PDFService.extract_text(str(file_path))
        if not text or len(text) < 100:
            file_path.unlink()
            raise HTTPException(status_code=400, detail="PDF 文本内容过少，请检查文件")

        # 解析案件信息
        case_info = PDFService.parse_case_info(text)

        # 生成默认值
        if not case_info["case_number"]:
            case_info["case_number"] = f"UPLOAD-{file_id[:8]}"

        if not case_info["title"]:
            case_info["title"] = f"用户上传案例 - {file.filename}"

        # 检查案号是否已存在
        result = await db.execute(
            select(Case).where(Case.case_number == case_info["case_number"])
        )
        if result.scalar_one_or_none():
            # 如果案号已存在，添加后缀
            case_info["case_number"] = f"{case_info['case_number']}-{file_id[:4]}"

        # 创建案例
        case = Case(
            case_number=case_info["case_number"],
            title=case_info["title"],
            court=case_info["court"],
            case_type=case_info["case_type"],
            judgment_date=case_info["judgment_date"],
            content=text,
            parties=case_info["parties"],
            is_real="upload",  # 标记为用户上传
            source=f"用户上传: {file.filename}"
        )

        db.add(case)
        await db.commit()
        await db.refresh(case)

        # 异步存储到向量数据库
        try:
            await vector_service.upsert_case(
                case_id=case.id,
                title=case.title,
                content=text,
                case_type=case.case_type,
                court=case.court,
                case_number=case.case_number
            )
        except Exception as e:
            # 向量存储失败不影响主流程
            import logging
            logging.warning(f"Failed to store uploaded case vector: {e}")

        return case

    except HTTPException:
        raise
    except Exception as e:
        # 清理文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    finally:
        # 关闭文件
        await file.close()


@router.post("/{case_id}/export-pdf")
async def export_analysis_pdf(
    case_id: int,
    perspective: str = Query("both", regex="^(both|professional|plain)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出分析报告为 PDF

    Args:
        case_id: 案例 ID
        perspective: 视角 (both/professional/plain)
            - both: 双视角
            - professional: 仅专业视角
            - plain: 仅普通人视角
    """
    # 获取案例
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 获取分析结果（从缓存读取）
    try:
        # 先检查缓存
        cache_result = await db.execute(
            select(CaseAnalysis).where(CaseAnalysis.case_id == case_id)
        )
        cached_analysis = cache_result.scalar_one_or_none()

        if not cached_analysis:
            raise HTTPException(status_code=400, detail="请先进行 AI 分析")

        # 使用缓存的分析结果
        analysis = cached_analysis.analysis_result

        # 准备案例信息
        case_info = {
            "title": case.title,
            "case_number": case.case_number,
            "court": case.court,
            "case_type": case.case_type,
            "judgment_date": str(case.judgment_date) if case.judgment_date else "",
        }

        # 生成 PDF
        pdf_bytes = PDFExportService.generate_analysis_pdf(
            case_info=case_info,
            analysis=analysis,
            perspective=perspective
        )

        # 生成文件名（URL 编码以支持中文）
        from urllib.parse import quote
        perspective_name = {
            "both": "双视角",
            "professional": "专业版",
            "plain": "普通人版"
        }
        filename = f"{case.case_number}_{perspective_name[perspective]}_分析报告.pdf"
        encoded_filename = quote(filename)

        # 返回 PDF
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
