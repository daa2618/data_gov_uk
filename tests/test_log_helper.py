from __future__ import annotations

import logging
import os
import pytest
from unittest.mock import patch

from data_gov_uk.utils.log_helper import (
    BasicLogger,
    AppLogger,
    DirectoryCreationError,
    _checkDirectory,
)


class TestCheckDirectory:
    def test_creates_missing_dir(self, tmp_path):
        target = str(tmp_path / "new_dir")
        result = _checkDirectory(target)
        assert os.path.isdir(result)

    def test_existing_dir_returns_path(self, tmp_path):
        result = _checkDirectory(str(tmp_path))
        assert result == str(tmp_path)

    def test_raises_on_failure(self):
        with patch("data_gov_uk.utils.log_helper.os.makedirs", side_effect=OSError("fail")):
            with pytest.raises(DirectoryCreationError):
                _checkDirectory("/impossible/path/that/will/fail")


class TestBasicLogger:
    def test_creates_logger_instance(self):
        bl = BasicLogger(logger_name="test_basic", log_directory=None, verbose=False)
        assert isinstance(bl.logger, logging.Logger)

    def test_level_is_set(self):
        bl = BasicLogger(
            logger_name="test_level",
            log_level=logging.DEBUG,
            log_directory=None,
            verbose=False,
        )
        assert bl.logger.level == logging.DEBUG

    def test_no_directory_skips_file_handler(self):
        bl = BasicLogger(
            logger_name="test_no_dir",
            log_directory=None,
            verbose=False,
            log_to_console=False,
        )
        file_handlers = [
            h for h in bl.logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 0


class TestAppLogger:
    def test_console_handler_added(self):
        al = AppLogger(
            logger_name="test_console",
            log_directory=None,
            log_to_console=True,
            verbose=False,
        )
        stream_handlers = [
            h for h in al.logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(stream_handlers) >= 1

    def test_no_console_handler(self):
        al = AppLogger(
            logger_name="test_no_console",
            log_directory=None,
            log_to_console=False,
            verbose=False,
        )
        assert len(al.logger.handlers) == 0

    def test_close_removes_handlers(self):
        al = AppLogger(
            logger_name="test_close",
            log_directory=None,
            log_to_console=True,
            verbose=False,
        )
        assert len(al.logger.handlers) > 0
        al.close()
        assert len(al.logger.handlers) == 0

    def test_file_handler_with_tmp_dir(self, tmp_path):
        al = AppLogger(
            logger_name="test_file",
            log_directory=str(tmp_path),
            log_to_console=False,
            verbose=False,
        )
        file_handlers = [
            h for h in al.logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
        al.close()
