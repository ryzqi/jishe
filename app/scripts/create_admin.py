"""
创建超级管理员账户脚本

用法:
python -m app.scripts.create_admin
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import select
from db.database import async_db_session
from models.user import User
from models.role import Role
from models.user_role import UserRole
from core.password import get_password_hash
from loguru import logger


async def create_super_admin():
    """创建超级管理员用户"""
    # 创建会话
    async with async_db_session() as session:
        # 检查用户是否已存在
        query = select(User).where(User.username == "admin")
        result = await session.execute(query)
        existing_user = result.scalars().first()
        
        if existing_user:
            logger.info("超级管理员 'admin' 已存在")
            return
        
        # 检查角色是否存在
        query = select(Role).where(Role.role_id == 1)
        result = await session.execute(query)
        super_admin_role = result.scalars().first()
        
        if not super_admin_role:
            # 创建超级管理员角色
            super_admin_role = Role(role_id=1, role_name="超级管理员")
            session.add(super_admin_role)
            await session.flush()
            logger.info("已创建超级管理员角色")
        
        # 创建超级管理员用户
        admin_user = User(
            username="admin",
            password=get_password_hash("123456")
        )
        session.add(admin_user)
        await session.flush()
        
        # 分配超级管理员角色
        user_role = UserRole(user_id=admin_user.id, role_id=1)
        session.add(user_role)
        
        await session.commit()
        logger.success(f"已成功创建超级管理员用户 'admin'，ID: {admin_user.id}")


async def main():
    """主函数"""
    logger.info("开始创建超级管理员...")
    await create_super_admin()
    logger.info("完成")


if __name__ == "__main__":
    asyncio.run(main()) 