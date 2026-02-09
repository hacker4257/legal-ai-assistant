"""
法律条文数据导入脚本

将 data/laws/ 目录下的法律条文 JSON 文件导入到：
1. PostgreSQL 数据库 (LegalStatute 表)
2. Qdrant 向量数据库 (legal_statutes collection)

使用方法：
    python -m scripts.import_laws
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.models import LegalStatute
from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service


# 法律条文专用 Collection
STATUTES_COLLECTION = "legal_statutes"


async def init_statutes_collection():
    """初始化法律条文向量 Collection"""
    from qdrant_client.http import models

    try:
        client = await vector_service._get_client()

        # 检查是否存在
        collections = client.get_collections().collections
        exists = any(c.name == STATUTES_COLLECTION for c in collections)

        if not exists:
            client.create_collection(
                collection_name=STATUTES_COLLECTION,
                vectors_config=models.VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE
                )
            )

            # 创建索引
            client.create_payload_index(
                collection_name=STATUTES_COLLECTION,
                field_name="law_category",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            client.create_payload_index(
                collection_name=STATUTES_COLLECTION,
                field_name="law_name",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            # 全文搜索索引
            client.create_payload_index(
                collection_name=STATUTES_COLLECTION,
                field_name="content",
                field_schema=models.TextIndexParams(
                    type="text",
                    tokenizer=models.TokenizerType.MULTILINGUAL,
                    min_token_len=2,
                    max_token_len=20
                )
            )

            print(f"✅ Created collection: {STATUTES_COLLECTION}")
        else:
            print(f"ℹ️  Collection {STATUTES_COLLECTION} already exists")

        return True
    except Exception as e:
        print(f"❌ Failed to init collection: {e}")
        return False


async def import_law_file(session: AsyncSession, file_path: Path) -> tuple[int, int]:
    """导入单个法律文件

    Returns:
        (成功数, 失败数)
    """
    from qdrant_client.http import models

    print(f"\n📂 Processing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    law_name = data['law_name']
    law_category = data['law_category']
    effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d').date() if data.get('effective_date') else None
    source = data.get('source', '')

    success = 0
    failed = 0
    client = await vector_service._get_client()

    for article in data['articles']:
        try:
            # 检查是否已存在
            existing = await session.execute(
                select(LegalStatute).where(
                    LegalStatute.law_name == law_name,
                    LegalStatute.article_number == article['article_number']
                )
            )
            if existing.scalar_one_or_none():
                print(f"  ⏭️  Skip existing: {article['article_number']}")
                continue

            # 创建数据库记录
            statute = LegalStatute(
                law_name=law_name,
                law_category=law_category,
                chapter=article.get('chapter', ''),
                article_number=article['article_number'],
                article_title=article.get('article_title', ''),
                content=article['content'],
                keywords=article.get('keywords', []),
                effective_date=effective_date,
                source=source
            )
            session.add(statute)
            await session.flush()  # 获取 ID

            # 生成向量并存入 Qdrant
            text_for_embedding = f"{law_name} {article['article_number']}\n{article['content']}"
            embedding = await embedding_service.generate_embedding(text_for_embedding)

            if embedding:
                client.upsert(
                    collection_name=STATUTES_COLLECTION,
                    points=[
                        models.PointStruct(
                            id=statute.id,
                            vector=embedding,
                            payload={
                                "statute_id": statute.id,
                                "law_name": law_name,
                                "law_category": law_category,
                                "article_number": article['article_number'],
                                "chapter": article.get('chapter', ''),
                                "content": article['content'],
                                "keywords": article.get('keywords', [])
                            }
                        )
                    ]
                )

            print(f"  ✅ Imported: {article['article_number']}")
            success += 1

        except Exception as e:
            print(f"  ❌ Failed {article['article_number']}: {e}")
            failed += 1

    await session.commit()
    return success, failed


async def import_all_laws():
    """导入所有法律文件"""
    print("=" * 60)
    print("法律条文导入工具")
    print("=" * 60)

    # 检查 Qdrant
    print("\n[1/3] 检查向量数据库连接...")
    if not await vector_service.is_available():
        print("❌ Qdrant 不可用，请确保服务已启动")
        return

    # 初始化 Collection
    print("[2/3] 初始化法律条文 Collection...")
    await init_statutes_collection()

    # 数据库连接
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 扫描法律文件
    laws_dir = Path(__file__).parent.parent / 'data' / 'laws'
    if not laws_dir.exists():
        print(f"❌ 法律数据目录不存在: {laws_dir}")
        return

    law_files = list(laws_dir.glob('*.json'))
    print(f"\n[3/3] 发现 {len(law_files)} 个法律文件")

    total_success = 0
    total_failed = 0

    async with async_session() as session:
        for file_path in law_files:
            success, failed = await import_law_file(session, file_path)
            total_success += success
            total_failed += failed

    # 统计
    print("\n" + "=" * 60)
    print("导入完成！")
    print(f"  成功: {total_success}")
    print(f"  失败: {total_failed}")
    print("=" * 60)


async def verify_import():
    """验证导入结果"""
    print("\n验证导入结果...")

    # 测试检索
    test_queries = [
        "劳动合同解除",
        "离婚财产分割",
        "违约责任赔偿",
        "加班工资",
        "交通事故赔偿",
        "醉酒驾驶",
        "七天无理由退货",
        "诈骗罪",
        "正当防卫",
        "医疗费误工费"
    ]

    from qdrant_client.http import models

    client = await vector_service._get_client()

    for query in test_queries:
        embedding = await embedding_service.generate_embedding(query)
        if not embedding:
            continue

        results = client.search(
            collection_name=STATUTES_COLLECTION,
            query_vector=embedding,
            limit=3
        )

        print(f"\n🔍 搜索: '{query}'")
        for r in results:
            print(f"  [{r.score:.3f}] {r.payload['law_name']} {r.payload['article_number']}")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="导入法律条文到数据库和向量库")
    parser.add_argument("--verify", action="store_true", help="导入后验证")

    args = parser.parse_args()

    await import_all_laws()

    if args.verify:
        await verify_import()


if __name__ == "__main__":
    asyncio.run(main())
