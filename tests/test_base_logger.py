
"""
Tests for the base_logger module.
"""
import unittest
import logging
import os
from unittest.mock import patch
import importlib
import base_logger

from base_logger import CustomFormatter, logger


class TestBaseLogger(unittest.TestCase):
    """
    Test cases for the base_logger module.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_custom_formatter(self):
        """
        Test the custom formatter.
        """
        formatter = CustomFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        formatted_message = formatter.format(record)
        self.assertIn('Test message', formatted_message)
        self.assertIn('test.py:10', formatted_message)

    @patch('base_logger.logging.StreamHandler')
    def test_logger_stream_handler(self, mock_stream_handler):
        """
        Test the logger's stream handler.
        """
        mock_stream_handler.return_value.level = logging.DEBUG
        with patch.dict(os.environ, {'LOG_HANDLER': 'Stream',
                                     'LOGLEVEL': 'DEBUG'}):
            importlib.reload(base_logger)
            self.assertEqual(len(logger.handlers), 1)
            self.assertIsInstance(logger.handlers[0],
                                  type(mock_stream_handler.return_value))
            self.assertEqual(logger.level, logging.DEBUG)

    @patch('base_logger.logging.FileHandler')
    def test_logger_file_handler(self, mock_file_handler):
        """
        Test the logger's file handler.
        """
        mock_file_handler.return_value.level = logging.INFO
        with patch.dict(os.environ, {'LOG_HANDLER': 'File',
                                     'LOG_FILE_PATH': 'test.log',
                                     'LOGLEVEL': 'INFO'}):
            importlib.reload(base_logger)
            self.assertEqual(len(logger.handlers), 1)
            self.assertIsInstance(logger.handlers[0],
                                  type(mock_file_handler.return_value))
            self.assertEqual(logger.level, logging.INFO)
            mock_file_handler.assert_called_with('test.log', mode='a')


if __name__ == '__main__':
    unittest.main()
