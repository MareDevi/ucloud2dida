"""
滴答清单项目列表查询工具

用于获取用户的滴答清单项目列表及其ID，方便配置同步目标项目。
"""

import asyncio
from dida365 import Dida365Client
from src.ucloud2dida.utils.logger import logger

async def get_projects_from_client():
    """获取并显示用户的所有滴答清单项目"""
    client = Dida365Client()
    
    try:
        if not client.auth.token:
            logger.info("未检测到认证令牌，开始首次认证")
            await client.authenticate()
            logger.info("认证成功")

        logger.info("正在获取项目列表...")
        projects = await client.get_projects()
        
        if not projects:
            logger.warning("未找到任何项目")
            return
        
        logger.info(f"找到 {len(projects)} 个项目:")
        print("\n可用的项目列表:")
        print("-" * 50)
        for project in projects:
            print(f"项目名称: {project.name}")
            print(f"项目 ID: {project.id}")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"获取项目列表时发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(get_projects_from_client())
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
