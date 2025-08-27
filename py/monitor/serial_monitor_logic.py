#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Real serial port monitor logic for ESP32 devices.
Handles actual serial communication and data capture from hardware.
Inherits from BaseMonitorLogic for common functionality.
'''

import logging
import threading
import subprocess
import select
import time

from py.monitor.base_monitor_logic import BaseMonitorLogic
from py.commands import ShellCommand
from py.log.rich_log_handler import LogSource, RichLogHandler

class SerialMonitorLogic(BaseMonitorLogic):
    """
    Real serial port monitor logic for ESP32 devices.
    Handles actual serial communication and data capture from hardware.
    Inherits common functionality from BaseMonitorLogic.
    """

    def _run_monitor(self, port: str, stop_event: threading.Event) -> None:
        """
        Internal method to run real serial monitor and capture output.
        Executes idf.py monitor command and captures real-time serial data.
        
        Args:
            port: Port identifier being monitored
            serial_logger: Logger instance for output
            stop_event: Event to check for stop signal
        """
        serial_logger = RichLogHandler.get_logger(LogSource.SERIAL, port)
        # Create monitor command using idf.py monitor for better compatibility
        monitor_command = ShellCommand(
            name=f"Monitor port '/dev/{port}'",
            command=f"bash -c 'source {self._get_idf_setup_path()} && idf.py -p /dev/{port} monitor'",
            logger=serial_logger
        )
        
        try:
            serial_logger.info(f"Running command: {monitor_command.name} ({monitor_command.command})")
            
            process = subprocess.Popen(
                monitor_command.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  # Use binary mode for non-blocking reads
                bufsize=0    # Disable buffering
            )
            
            # Use custom log format for this monitor
            with self.custom_log_format(port):
                # Main loop runs until the process completes or is stopped
                while process.poll() is None:
                    # Check if monitor was stopped
                    if stop_event.is_set():
                        serial_logger.info(f"Monitor on port {port} was stopped")
                        break
                    
                    # Wait for data from either stdout or stderr with timeout
                    readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)

                    # Process all available outputs
                    for stream in readable:
                        # Read all available data from the current stream
                        while True:
                            line = stream.readline()
                            if not line:  # No more data available
                                break
                            # Convert binary data to text
                            text = line.decode('utf-8', errors='ignore').strip()
                            if text:  # Only log non-empty lines
                                if stream == process.stdout:
                                    serial_logger.info(text)
                                else:
                                    serial_logger.warning(text)
                    
                    # Short pause to prevent CPU overload
                    time.sleep(0.01)
                
                # Process has finished, read remaining output
                for line in iter(process.stdout.readline, b''):
                    text = line.decode('utf-8', errors='ignore').strip()
                    if text:
                        serial_logger.info(f'{text}')
                
                for line in iter(process.stderr.readline, b''):
                    text = line.decode('utf-8', errors='ignore').strip()
                    if text:
                        serial_logger.warning(f'{text}')
                
                # Close the streams
                process.stdout.close()
                process.stderr.close()
                
                # Wait for the process to complete and get the exit code
                process.wait()
                
                if process.returncode != 0:
                    serial_logger.warning(f"Monitor on port {port} stopped with exit code {process.returncode}")
                else:
                    serial_logger.info(f"Monitor on port {port} completed successfully")
                    
        except Exception as e:
            serial_logger.error(f"Monitor on port {port} failed with exception: {e}")
            import traceback
            serial_logger.debug(traceback.format_exc())
        finally:
            # Clean up - this is now handled by BaseMonitorLogic
            # The thread will be removed from active_monitors when stop_monitor is called
            pass

    def _get_monitor_name(self) -> str:
        """
        Return the monitor type name for identification.
        
        Returns:
            String identifier for the serial monitor type
        """
        return "SERIAL"

    def _get_idf_setup_path(self) -> str:
        """
        Get the IDF setup path for this monitor instance.
        This method should be overridden or the path should be passed during initialization.
        
        Returns:
            Path to ESP-IDF setup script
        """
        # Default path - can be overridden by setting self.idf_setup_path
        return getattr(self, 'idf_setup_path', '~/esp/v5.4.1/esp-idf/export.sh')

    def start_monitor(self, port: str, idf_setup_path: str, serial_logger) -> bool:
        """
        Start monitoring on given port with IDF setup path.
        Overrides base method to store IDF setup path for later use.
        
        Args:
            port: Port identifier to monitor
            idf_setup_path: Path to ESP-IDF setup script
            serial_logger: Logger instance for output
            
        Returns:
            True if monitor started successfully, False otherwise
        """
        # Store IDF setup path for use in _run_monitor
        self.idf_setup_path = idf_setup_path
        
        # Call base class method
        return super().start_monitor(port, idf_setup_path, serial_logger)
