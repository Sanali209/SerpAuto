import sys
from typing import Optional

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging

    # Simple mock for loguru logger
    class MockLogger:
        def __init__(self):
            self.logger = logging.getLogger("serpentine")
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)s - %(message)s')
            handler.setFormatter(formatter)
            if not self.logger.handlers:
                self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

        def add(self, *args, **kwargs):
            pass

        def remove(self, *args, **kwargs):
            pass

        def bind(self, **kwargs):
            return self

        def debug(self, msg, *args, **kwargs):
            self.logger.debug(str(msg).format(*args, **kwargs))

        def info(self, msg, *args, **kwargs):
            self.logger.info(str(msg).format(*args, **kwargs))

        def warning(self, msg, *args, **kwargs):
            self.logger.warning(str(msg).format(*args, **kwargs))

        def error(self, msg, *args, **kwargs):
            self.logger.error(str(msg).format(*args, **kwargs))

        def exception(self, msg, *args, **kwargs):
            self.logger.exception(str(msg).format(*args, **kwargs))

    logger = MockLogger()

def configure_logging(level: str = "INFO", log_file: Optional[str] = "serpentine.log"):
    """
    Configures the Loguru logger for the Serpentine Engine.

    Args:
        level: The minimum log level to capture (e.g., "DEBUG", "INFO", "WARNING").
        log_file: Path to the log file. If None, file logging is disabled.
    """
    if LOGURU_AVAILABLE:
        logger.remove()  # Remove default handler

        # Add console handler with custom format
        logger.add(
            sys.stderr,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )

        # Add file handler if specified
        if log_file:
            logger.add(
                log_file,
                rotation="10 MB",
                retention="1 week",
                level="DEBUG",  # Always log DEBUG to file
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra} | {message}"
            )

        # Bind phase context if needed (can be used as logger.bind(phase=1).info(...))
        return logger.bind(system="core")
    else:
        # Configure standard logging level if needed
        # MockLogger already configures basic handler
        return logger
