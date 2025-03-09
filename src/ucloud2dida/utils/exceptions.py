class UCloud2DidaError(Exception):
    """基础异常类"""

    pass


class AuthenticationError(UCloud2DidaError):
    """认证相关错误"""

    pass


class APIError(UCloud2DidaError):
    """API调用错误"""

    pass


class SyncError(UCloud2DidaError):
    """同步过程错误"""

    pass


class ConfigError(UCloud2DidaError):
    """配置相关错误"""

    pass


# 导出所有异常类
__all__ = [
    "UCloud2DidaError",
    "AuthenticationError",
    "APIError",
    "SyncError",
    "ConfigError",
]
