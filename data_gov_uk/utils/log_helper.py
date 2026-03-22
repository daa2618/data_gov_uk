from __future__ import annotations

import logging


def get_logger(name: str, level: int = logging.WARNING) -> logging.Logger:
    """Get or create a named logger with a console handler."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


class BasicLogger:
    """Thin compatibility wrapper around stdlib logging."""

    def __init__(
        self,
        logger_name: str = "app",
        log_level: int = logging.WARNING,
        verbose: bool = False,
        log_directory: str | None = None,
        **kwargs,
    ):
        self.logger = get_logger(logger_name, log_level)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, exc_info=None, **kwargs):
        self.logger.error(message, *args, exc_info=exc_info, **kwargs)

    def critical(self, message: str, *args, exc_info=None, **kwargs):
        self.logger.critical(message, *args, exc_info=exc_info, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs)

    def close(self) -> None:
        """Remove all handlers from this logger."""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
