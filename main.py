import asyncio
from src.ucloud2dida.utils.logger import setup_logger
from src.ucloud2dida.core.sync import perform_sync_cycle
from src.ucloud2dida.utils.config import config

async def main():
    """主程序入口"""
    logger = setup_logger(config.log_level)
    logger.debug("日志级别已设置")

    # 只执行一次同步服务
    await perform_sync_cycle(None, config.sync_interval, config.max_retries)
    logger.info("同步服务已停止")

if __name__ == "__main__":
    logger = setup_logger(config.log_level)
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"程序异常退出: {str(e)}")
        raise
