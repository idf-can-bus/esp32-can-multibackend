#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Configuration for a system command process.
Includes command line, output color, and other display parameters.
'''

class ShellCommandConfig:
    """
    Configuration for a system command process.
    Includes command line, output color, and other display parameters.
    """
    def __init__(self, name: str, command: str):
        """
        Initialize the configuration for a system command.
        :param name: Human-readable name for the command.
        :param command: Command line to execute.
        """
        self.name = name or command
        self.command = command
        