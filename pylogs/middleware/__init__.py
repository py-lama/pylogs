"""Middleware for PyLogs integration with web frameworks."""

try:
    from pylogs.middleware.flask_middleware import FlaskLoggingMiddleware
    __all__ = ["FlaskLoggingMiddleware"]
except ImportError:
    __all__ = []

try:
    from pylogs.middleware.fastapi_middleware import FastAPILoggingMiddleware
    __all__.append("FastAPILoggingMiddleware")
except ImportError:
    pass
