"""重新创建测试用户"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import AsyncSessionLocal
from app.models.models import User
from app.core.security import get_password_hash
from sqlalchemy import select


async def recreate_user():
    """重新创建测试用户"""
    async with AsyncSessionLocal() as db:
        try:
            # 删除旧用户
            result = await db.execute(select(User).where(User.username == "testuser"))
            old_user = result.scalar_one_or_none()
            if old_user:
                await db.delete(old_user)
                await db.commit()
                print("已删除旧用户")

            # 创建新用户
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash=get_password_hash("123456"),
                user_type="individual"
            )
            db.add(user)
            await db.commit()
            print("✓ 成功创建测试用户")
            print("  用户名: testuser")
            print("  密码: 123456")

        except Exception as e:
            await db.rollback()
            print(f"✗ 创建失败: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(recreate_user())
