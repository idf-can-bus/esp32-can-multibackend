#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Classes for asynchronous execution and management of system commands,
with real-time output streaming to RichText widgets.
'''
from typing import Callable, Any
import asyncio

class SystemCommandConfig:
    """
    Configuration for a system command process.
    Includes command line, output color, and other display parameters.
    """
    def __init__(self, command: str, color: str, max_lines: int = 1000, update_interval: float = 0.1):
        """
        Initialize the configuration for a system command.
        :param command: Command line to execute.
        :param color: Output color for display.
        :param max_lines: Maximum number of lines to keep in output.
        :param update_interval: Interval for output updates.
        """
        self.command = command
        self.color = color
        self.max_lines = max_lines
        self.update_interval = update_interval


class SystemCommandProcess:
    """
    Manages the execution of a system command and keeps a registry of all instances.
    Supports asynchronous output streaming, pausing, resuming, and termination.
    """
    _instances = set()

    def __init__(self, config: SystemCommandConfig, output_callback: Callable[[str, str], Any]):
        """
        Initialize the process manager.
        :param config: Configuration for the system command.
        :param output_callback: Callback for output lines.
        """
        self.config = config
        self.output_callback = output_callback
        self.process = None
        self.running = False
        self.pause_output_flag = False

    async def start(self) -> None:
        """
        Start the system command process asynchronously and stream output.
        Automatically registers the instance.
        """
        self.process = await asyncio.create_subprocess_shell(
            self.config.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        self.running = True
        SystemCommandProcess._instances.add(self)
        try:
            await asyncio.wait_for(
                asyncio.gather(
                    self._read_stream(self.process.stdout, self.config.color),
                    self._read_stream(self.process.stderr, "red")
                ),
                timeout=300  # 5 minut timeout
            )
        except Exception as e:
            self.output_callback(f"Error: {e}", "red")
        self.running = False
        SystemCommandProcess._instances.discard(self)

    async def _read_stream(self, stream, color: str) -> None:
        """
        Asynchronously read lines from a stream and send them to the output callback.
        :param stream: The output stream (stdout or stderr).
        :param color: Color for the output.
        """
        while self.running and stream:
            if self.pause_output_flag:
                await asyncio.sleep(0.1)
                continue
            line = await stream.readline()
            if not line:
                break
            
            # If the callback supports async writing, use it
            if hasattr(self.output_callback, 'async_write'):
                await self.output_callback.async_write(line.decode("utf-8").strip())
            else:
                # Fallback for old callbacks
                self.output_callback(line.decode("utf-8").strip(), color)

    def pause_output(self) -> None:
        """
        Pause streaming output to the output callback.
        """
        self.pause_output_flag = True

    def resume_output(self) -> None:
        """
        Resume streaming output to the output callback.
        """
        self.pause_output_flag = False

    def terminate(self) -> None:
        """
        Terminate the running process and unregister the instance.
        """
        if self.process and self.running:
            self.process.terminate()
            self.running = False
            SystemCommandProcess._instances.discard(self)

    def is_running(self) -> bool:
        """
        Check if the process is still running.
        :return: True if running, False otherwise.
        """
        return self.running and self.process and self.process.returncode is None

    @classmethod
    def terminate_all(cls) -> None:
        """
        Terminate all running processes.
        """
        for proc in list(cls._instances):
            proc.terminate()

    @classmethod
    def get_running_processes(cls) -> list:
        """
        Get a list of all currently running processes.
        :return: List of running SystemCommandProcess instances.
        """
        return [p for p in cls._instances if p.is_running()]

