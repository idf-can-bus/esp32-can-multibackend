#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Base monitor logic class providing common functionality for all monitor implementations.
Handles thread management, start/stop operations, and log format switching.
'''

import logging
import threading
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from py.log.rich_log_handler import LogSource, RichLogHandler

serial_logger = RichLogHandler.get_logger(LogSource.SERIAL)

class BaseMonitorLogic(ABC):
    """
    Base class for all monitor logic implementations.
    Provides common functionality for thread management, start/stop operations,
    and log format switching. Derived classes must implement the actual
    monitoring logic.
    """

    def __init__(self):
        # Active monitoring processes - key: port, value: (thread, stop_event)
        self.active_monitors = {}
        self.monitor_lock = threading.Lock()
        self.original_format = None

    @contextmanager
    def custom_log_format(self, port: str):
        """
        Context manager for custom log format with port prefix.
        Temporarily changes the log format to include port identification.
        Automatically restores the original format when exiting the context.
        """
        try:
            # Store original format
            root_logger = logging.getLogger()
            if root_logger.handlers:
                self.original_format = root_logger.handlers[0].formatter._fmt
            
            # Create custom formatter with port prefix
            custom_format = f'%(levelname)s: {port} %(message)s'
            custom_formatter = logging.Formatter(custom_format)
            
            # Apply custom formatter to all handlers
            for handler in root_logger.handlers:
                handler.setFormatter(custom_formatter)
            
            yield  # Execute the monitored code
            
        finally:
            # Restore original format
            if self.original_format:
                original_formatter = logging.Formatter(self.original_format)
                for handler in root_logger.handlers:
                    handler.setFormatter(original_formatter)

    def stop_all_monitors(self) -> None:
        """
        Stop all active monitoring processes.
        Signals all monitor threads to stop and waits for them to finish.
        """
        with self.monitor_lock:
            for port, (thread, stop_event) in self.active_monitors.items():
                serial_logger.info(f"Stopping {self._get_monitor_name()} monitor on port {port}")
                stop_event.set()  # Signal thread to stop
                
                # Wait for thread to finish
                if thread.is_alive():
                    thread.join(timeout=1)
            
            self.active_monitors.clear()
            serial_logger.info(f"All {self._get_monitor_name()} monitors stopped")

    def stop_monitor(self, port: str, prompt_char: str = '🗙👁️') -> bool:
        """
        Stop monitoring on specific port.
        
        Args:
            port: Port identifier to stop monitoring
            prompt_char: Character to prefix log messages
            
        Returns:
            True if monitor was stopped, False if not found
        """
        with self.monitor_lock:
            if port in self.active_monitors:
                thread, stop_event = self.active_monitors[port]
                serial_logger.info(f"Stopping {self._get_monitor_name()} monitor on port {port}")
                
                stop_event.set()  # Signal thread to stop
                
                # Wait for thread to finish
                if thread.is_alive():
                    thread.join(timeout=1)
                
                del self.active_monitors[port]
                serial_logger.info(f"{self._get_monitor_name()} monitor on port {port} stopped")
                return True
            return False

    def is_monitoring(self, port: str) -> bool:
        """
        Check if port is being monitored.
        
        Args:
            port: Port identifier to check
            
        Returns:
            True if port is being monitored, False otherwise
        """
        with self.monitor_lock:
            return port in self.active_monitors

    def start_monitor(self, port: str, idf_setup_path: str, serial_logger) -> bool:
        """
        Start monitoring on given port.
        Creates a new thread for monitoring and stores it for later management.
        
        Args:
            port: Port identifier to monitor
            idf_setup_path: Path to ESP-IDF setup script (unused in base class)
            serial_logger: Logger instance for output
            
        Returns:
            True if monitor started successfully, False otherwise
        """
        if not port:
            serial_logger.error("No port specified for monitoring")
            return False

        # Stop existing monitor on this port if running
        if self.is_monitoring(port):
            serial_logger.info(f"Port {port} is already being monitored")
            return False

        serial_logger.info(f"Starting {self._get_monitor_name()} monitor on port '/dev/{port}'")
        
        # Create stop event for this monitor
        stop_event = threading.Event()
        
        # Create and start monitor thread
        thread = self._create_monitor_thread(port, serial_logger, stop_event)
        thread.daemon = True
        
        # Store thread and stop event for later termination
        with self.monitor_lock:
            self.active_monitors[port] = (thread, stop_event)
        
        thread.start()
        return True

    def _create_monitor_thread(self, port: str, serial_logger, stop_event: threading.Event) -> threading.Thread:
        """
        Create a monitor thread for the given port.
        This method can be overridden by derived classes to customize thread creation.
        
        Args:
            port: Port identifier to monitor
            serial_logger: Logger instance for output
            stop_event: Event to signal thread to stop
            
        Returns:
            Thread object that will run the monitor
        """
        return threading.Thread(
            target=self._run_monitor,
            args=(port, stop_event)
        )

    @abstractmethod
    def _run_monitor(self, port: str, stop_event: threading.Event) -> None:
        """
        Abstract method that must be implemented by derived classes.
        Contains the actual monitoring logic for a specific port.
        
        Args:
            port: Port identifier being monitored
            stop_event: Event to check for stop signal
        """
        pass

    @abstractmethod
    def _get_monitor_name(self) -> str:
        """
        Abstract method that must return the monitor type name.
        Used for logging and identification purposes.
        
        Returns:
            String identifier for the monitor type (e.g., "FAKE", "SERIAL")
        """
        pass

    def get_active_monitor_count(self) -> int:
        """
        Get the number of currently active monitors.
        
        Returns:
            Number of active monitors
        """
        with self.monitor_lock:
            return len(self.active_monitors)

    def get_active_ports(self) -> list[str]:
        """
        Get list of ports that are currently being monitored.
        
        Returns:
            List of port identifiers
        """
        with self.monitor_lock:
            return list(self.active_monitors.keys())
