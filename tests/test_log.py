"""Test log functions."""
import logging
from pathlib import Path

import log


def test_get_project_root_dir():
    path = Path(__file__).absolute().parent.parent
    assert log.get_project_root_dir() == str(path)


def test_logging():
    log.init_logger()
    assert logging.getLogger()
