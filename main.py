import asyncio
import signal
import platform
from src.ucloud2dida.utils.logger import setup_logger
from src.ucloud2dida.core.sync import perform_sync_cycle
from src.ucloud2dida.utils.config import config


async def main():
    """主程序入口"""
    # 设置日志级别
    logger = setup_logger(config.log_level)
    logger.debug("日志级别已设置")

    shutdown_event = asyncio.Event()

    def signal_handler():
        logger.info("收到终止信号，准备退出...")
        shutdown_event.set()

    system = platform.system()
    loop = asyncio.get_running_loop()

    if system == "Windows":
        signal.signal(signal.SIGINT, lambda _, __: signal_handler())
        logger.info("运行在Windows系统上，已设置SIGINT (Ctrl+C) 信号处理")
    else:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
        logger.info(f"运行在{system}系统上，已设置SIGINT和SIGTERM信号处理")

    logger.info(f"同步服务启动，间隔时间设置为 {config.sync_interval} 秒")

    while not shutdown_event.is_set():
        if not await perform_sync_cycle(
            shutdown_event, config.sync_interval, config.max_retries
        ):
            break

    logger.info("同步服务已停止")


if __name__ == "__main__":
    logger = setup_logger(config.log_level)
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"程序异常退出: {str(e)}")
        raise
