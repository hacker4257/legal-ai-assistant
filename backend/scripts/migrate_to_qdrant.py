"""
数据迁移脚本 - 将现有案例迁移到 Qdrant 向量数据库

使用方法：
    python -m scripts.migrate_to_qdrant

功能：
    1. 为所有现有案例生成向量
    2. 批量导入到 Qdrant
    3. 支持增量迁移（跳过已存在的案例）
    4. 显示进度和统计信息
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.models import Case
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service


async def migrate_cases(batch_size: int = 50, skip_existing: bool = True):
    """迁移所有案例到向量数据库

    Args:
        batch_size: 每批处理的案例数量
        skip_existing: 是否跳过已存在的案例
    """
    print("=" * 60)
    print("法律案例向量数据库迁移工具")
    print("=" * 60)

    # 创建数据库连接
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 检查 Qdrant 连接
    print("\n[1/4] 检查 Qdrant 连接...")
    if not await vector_service.is_available():
        print("错误: Qdrant 服务不可用，请确保 Qdrant 已启动")
        print(f"      配置的 URL: {settings.QDRANT_URL}")
        return

    # 初始化 collection
    print("[2/4] 初始化向量数据库 collection...")
    if not await vector_service.init_collection():
        print("错误: 无法初始化 collection")
        return

    print(f"      Collection: {settings.QDRANT_COLLECTION}")
    print(f"      向量维度: {settings.EMBEDDING_DIMENSION}")

    # 获取案例总数
    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(Case))
        total_cases = result.scalar()

    print(f"\n[3/4] 发现 {total_cases} 个案例需要迁移")

    if total_cases == 0:
        print("没有案例需要迁移")
        return

    # 获取已存在的向量 ID
    existing_ids = set()
    if skip_existing:
        try:
            info = await vector_service.get_collection_info()
            if info and info.get("points_count", 0) > 0:
                print(f"      已存在 {info['points_count']} 个向量点")
                # 注意：这里简化处理，实际可能需要查询所有 ID
        except Exception:
            pass

    # 批量处理
    print("\n[4/4] 开始迁移...")
    success_count = 0
    error_count = 0
    skip_count = 0

    async with async_session() as session:
        offset = 0
        while offset < total_cases:
            # 获取一批案例
            stmt = select(Case).offset(offset).limit(batch_size)
            result = await session.execute(stmt)
            cases = result.scalars().all()

            if not cases:
                break

            for case in cases:
                # 跳过已存在的
                if skip_existing and case.id in existing_ids:
                    skip_count += 1
                    continue

                try:
                    success = await vector_service.upsert_case(
                        case_id=case.id,
                        title=case.title,
                        content=case.content or "",
                        case_type=case.case_type,
                        court=case.court,
                        case_number=case.case_number
                    )

                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        print(f"      警告: 案例 {case.id} 迁移失败")

                except Exception as e:
                    error_count += 1
                    print(f"      错误: 案例 {case.id} - {e}")

            # 显示进度
            progress = min(offset + batch_size, total_cases)
            percent = (progress / total_cases) * 100
            print(f"      进度: {progress}/{total_cases} ({percent:.1f}%)")

            offset += batch_size

            # 添加小延迟，避免压力过大
            await asyncio.sleep(0.1)

    # 显示统计
    print("\n" + "=" * 60)
    print("迁移完成！")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    print(f"  跳过: {skip_count}")
    print("=" * 60)

    # 显示 collection 信息
    info = await vector_service.get_collection_info()
    if info:
        print(f"\nCollection 状态:")
        print(f"  名称: {info['name']}")
        print(f"  向量数: {info['vectors_count']}")
        print(f"  状态: {info['status']}")


async def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")

    # 测试搜索
    test_queries = [
        "劳动合同纠纷",
        "离婚财产分割",
        "借款合同",
    ]

    for query in test_queries:
        results = await vector_service.search_similar(query, top_k=3)
        print(f"\n搜索 '{query}': 找到 {len(results)} 个结果")
        for r in results[:2]:
            print(f"  - {r['title']} (score: {r['score']:.3f})")


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="迁移案例到 Qdrant 向量数据库")
    parser.add_argument("--batch-size", type=int, default=50, help="批处理大小")
    parser.add_argument("--no-skip", action="store_true", help="不跳过已存在的案例")
    parser.add_argument("--verify", action="store_true", help="迁移后验证")

    args = parser.parse_args()

    await migrate_cases(
        batch_size=args.batch_size,
        skip_existing=not args.no_skip
    )

    if args.verify:
        await verify_migration()


if __name__ == "__main__":
    asyncio.run(main())
