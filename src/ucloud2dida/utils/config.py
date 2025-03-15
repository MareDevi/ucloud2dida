import os
from dotenv import load_dotenv
from .exceptions import ConfigError
from .logger import logger
import logging


class Config:
    """配置管理类"""

    def __init__(self):
        logger.info("正在初始化配置...")
        load_dotenv()
        self.validate_required_env()
        logger.info("配置初始化完成")

    def validate_required_env(self):
        """验证必需的环境变量"""
        required_vars = [
            "DIDA365_CLIENT_ID",
            "DIDA365_CLIENT_SECRET",
            "DIDA365_PROJECT_ID",
            "BUPT_ACCOUNT",
            "BUPT_PASSWORD",
        ]

        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            error_msg = f"缺少必需的环境变量: {', '.join(missing)}"
            logger.error(error_msg)
            raise ConfigError(error_msg)

        logger.debug("所有必需的环境变量验证通过")

    @property
    def sync_interval(self):
        """同步间隔（秒）"""
        interval = int(os.getenv("SYNC_INTERVAL_SECONDS", 3600))
        logger.debug(f"同步间隔设置为 {interval} 秒")
        return interval

    @property
    def max_retries(self):
        """最大重试次数"""
        retries = int(os.getenv("MAX_RETRIES", 3))
        logger.debug(f"最大重试次数设置为 {retries} 次")
        return retries

    @property
    def log_level(self):
        """获取日志级别设置"""
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        valid_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return valid_levels.get(level, logging.INFO)


# 创建全局配置实例
config = Config()
