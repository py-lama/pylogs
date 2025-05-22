"""Middleware for LogLama integration with web frameworks."""

try:
    from loglama.middleware.flask_middleware import FlaskLoggingMiddleware
    __all__ = ["FlaskLoggingMiddleware"]
except ImportError:
    __all__ = []

try:
    from loglama.middleware.fastapi_middleware import FastAPILoggingMiddleware
    __all__.append("FastAPILoggingMiddleware")
except ImportError:
    pass
