from __future__ import annotations

import logging

from data_gov_uk.utils.log_helper import BasicLogger, get_logger


class TestGetLogger:
    def test_returns_logger(self):
        logger = get_logger("test_returns")
        assert isinstance(logger, logging.Logger)

    def test_sets_level(self):
        logger = get_logger("test_level", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_adds_handler(self):
        logger = get_logger("test_handler")
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) >= 1

    def test_no_duplicate_handlers(self):
        name = "test_no_dup"
        logger1 = get_logger(name)
        count1 = len(logger1.handlers)
        logger2 = get_logger(name)
        assert len(logger2.handlers) == count1


class TestBasicLogger:
    def test_creates_logger_instance(self):
        bl = BasicLogger(logger_name="test_basic")
        assert isinstance(bl.logger, logging.Logger)

    def test_level_is_set(self):
        bl = BasicLogger(logger_name="test_bl_level", log_level=logging.DEBUG)
        assert bl.logger.level == logging.DEBUG

    def test_delegates_methods(self):
        bl = BasicLogger(logger_name="test_delegate", log_level=logging.DEBUG)
        # Should not raise
        bl.debug("debug msg")
        bl.info("info msg")
        bl.warning("warning msg")
        bl.error("error msg")
        bl.critical("critical msg")

    def test_close_removes_handlers(self):
        bl = BasicLogger(logger_name="test_close_bl")
        assert len(bl.logger.handlers) > 0
        bl.close()
        assert len(bl.logger.handlers) == 0

    def test_accepts_legacy_kwargs(self):
        """Ensure old-style kwargs (verbose, log_directory) don't raise."""
        bl = BasicLogger(
            logger_name="test_legacy",
            verbose=False,
            log_directory=None,
        )
        assert isinstance(bl.logger, logging.Logger)
