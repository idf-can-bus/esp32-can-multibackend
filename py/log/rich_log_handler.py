#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Custom logging handler for Textual RichLog (RichLogExtened) widget.
Provides real-time log message display in the GUI with proper formatting.
'''

import logging
import re
from enum import Enum
from textual.widgets import RichLog
from py.log.rich_log_extended import RichLogExtended

class LogSource(Enum):
    """
    Enumeration of log sources for consistent identification.
    Each source has an associated emoji and display name.
    """
    # Configuration and setup
    CONFIG = ("⚙️", "CONFIG")  # for all config related logs
    RECONFIG = ("✏", "RECONFIG")  # for reconfiguration related logs

    # Build and compilation
    COMPILE = ("⚒️", "COMPILE")
    BUILD = ("🔨", "BUILD")

    # Flash operations
    FLASH = ("⚡", "FLASH")

    # Monitor of serial port operations
    SERIAL = ("👁️", "SERIAL")
    FAKE_SERIAL = ("👻", "FAKE_MONITOR")

    # Python application
    PYTHON = ("🐍", "PYTHON")

    def __init__(self, emoji: str, display_name: str):
        self.emoji = emoji
        self.display_name = display_name


class RichLogHandler(logging.Handler):
    """
    Custom logging handler for RichLog (RichLogExtened)
    This class is used to log messages to a RichLog (RichLogExtened) widget
    It is used to display the log messages in a more readable format.
    """
    registered_loggers = {}
    _rich_log = None  # Shared RichLog (RichLogExtened) instance for all handlers

    # Pre-compiled regex patterns for automatic level detection
    # @TODO: implement level detection from message content
    # Currently used only for error and warning levels to avoid unintended level changes
    _level_patterns = {
        logging.ERROR: [
            re.compile(r'\b(error|Error|ERROR)\b'),
            re.compile(r'\b(failed|Failed|FAILED)\b'),
            re.compile(r'\b(exception|Exception|EXCEPTION)\b'),
            re.compile(r'\bE \(\d+\)\b'),  # ESP-IDF error format
        ],
        logging.WARNING: [
            re.compile(r'\b(warning|Warning|WARNING)\b'),
            re.compile(r'\b(warn|Warn|WARN)\b'),
            re.compile(r'\bW \(\d+\)\b'),  # ESP-IDF warning format
        ],
        logging.INFO: [
            re.compile(r'\b(info|Info|INFO)\b'),
            re.compile(r'\bI \(\d+\)\b'),  # ESP-IDF info format
        ]
    }

    # set RichLog or his subclass (like RichLogExtened) instance
    @classmethod
    def set_rich_log(cls, rich_log: RichLog):
        cls._rich_log = rich_log

    @classmethod
    def get_logger(cls, source: LogSource = LogSource.PYTHON, display_name: str = None):
        """
        Logger is defined by  LogSource and eventually display_name.
        display_name can be empty, or specify othe part of source (like port name).
        If logger is not registered, it is created wiht coresponding handler and registered.
        If logger is registered, it is returned.
        """
        logger_key = (source, display_name)
    
        # check if logger with given source and display_name is already registered
        try:
            return cls.registered_loggers[logger_key]
        except KeyError:
            # create handler for source
            handler = RichLogHandler(source, display_name)
            # Unique logger name
            logger_name = f"{source.display_name}.{display_name}" if display_name else source.display_name
            logger = logging.getLogger(logger_name)
            # Remove all existing handlers
            for h in logger.handlers[:]:  
                logger.removeHandler(h)
            logger.addHandler(handler)
            logger.propagate = False
            cls.registered_loggers[logger_key] = logger   
            return logger

    def __init__(self, source: LogSource = LogSource.PYTHON, display_name: str = None, extra_color: str = None):
        super().__init__()
        self._source = source
        self._source_display_name = display_name
        self._extra_color = extra_color

    def emit(self, record: logging.LogRecord):
        if self._rich_log:
            record = self._modify_record(record)
            msg = self.format(record)
            self._rich_log.write(msg)
            # Force refresh to ensure immediate display
            self._rich_log.refresh()

    def _modify_record(self, record: logging.LogRecord) -> logging.LogRecord:
        """
        Reformat record to include source and display_name
        """
        return self._modify_message(  # Modify the log message to include source emoji and display name
            self._modify_level(record) # Modify the log level from the message content if possible
        )

    def _modify_message(self, record: logging.LogRecord = None) -> logging.LogRecord:
        '''
        Modify the log message to include source emoji and display name
        If extra_color is set, add it to the message

        @TODO: add extra_color to the message
        '''
        if self._source_display_name:
            record.msg = f"{self._source.emoji} {self._source_display_name}: {record.msg}"
        else:
            record.msg = f"{self._source.emoji} {self._source.display_name}: {record.msg}"
        return record

    def _modify_level(self, record: logging.LogRecord = None) -> logging.LogRecord:
        """
        Attempt to detect log level from message content using regex patterns.
        If a pattern matches, the record's level is updated accordingly.
        """
        # @TODO: implement level detection from message content
        # Currently disabled to avoid unintended level changes

        # if record is None:
        #     return None
        # message = record.getMessage()
        # for level, patterns in self._level_patterns.items():
        #     for pattern in patterns:
        #         if pattern.search(message):
        #             record.levelno = level
        #             record.levelname = logging.getLevelName(level)
        #             return record
        return record
