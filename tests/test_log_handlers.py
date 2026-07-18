"""
Tests for log_handlers.py
"""

import logging
import unittest
from flask import Flask
from service.common.log_handlers import init_logging


class TestLogHandlers(unittest.TestCase):
    """log_handlers.py Test"""

    def test_formatter_is_set(self):
        """It should set a formatter on all handlers"""

        app = Flask(__name__)

        logger = logging.getLogger("test_logger")
        logger.handlers.clear()

        handler = logging.StreamHandler()
        logger.addHandler(handler)

        init_logging(app, "test_logger")

        self.assertIsNotNone(handler.formatter)
