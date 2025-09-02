#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Shell-based monitor logic using ShellCommandProcess.
Manages monitor processes for each port with button state synchronization.
Supports both real serial ports and fake monitoring for testing.
'''

import os
import glob
import asyncio
from typing import Dict, Optional
from py.shell_commands import ShellCommandConfig, ShellCommandProcess
from py.log.rich_log_handler import LogSource, RichLogHandler

class ShellMonitorLogic:
    """
    Shell-based monitor logic using ShellCommandProcess.
    Each port has one ShellCommandProcess that can be started/stopped.
    Button state is synchronized with process state.
    Supports both real serial ports and fake monitoring for testing.
    """
    
    def __init__(
        self, 
        idf_setup_path: str = "~/esp/v5.4.1/esp-idf/export.sh", 
        use_fake_monitor: bool = False
    ):
        """
        Initialize monitor logic.
        
        Args:
            idf_setup_path: Path to ESP-IDF setup script
            use_fake_monitor: If True, use fake monitor script instead of real serial port
        """
        self.idf_setup_path = os.path.expanduser(idf_setup_path)
        self.use_fake_monitor = use_fake_monitor
        
        # Active monitor processes - key: port, value: ShellCommandProcess
        self.active_monitors: Dict[str, ShellCommandProcess] = {}
        # Monitor button references - key: port, value: Button widget
        self.monitor_buttons: Dict[str, 'Button'] = {}
        
    def register_monitor_button(self, port: str, button: 'Button') -> None:
        """
        Register a monitor button for a specific port.
        
        Args:
            port: Port identifier
            button: Button widget to manage
        """
        self.monitor_buttons[port] = button
        self._update_button_state(port, False)  # Start in OFF state
        
    def start_monitor(self, port: str) -> bool:
        """
        Start monitoring on given port.
        
        Args:
            port: Port identifier to monitor
            
        Returns:
            True if monitor started successfully, False otherwise
        """
        if port in self.active_monitors:
            # Monitor already running
            return False
            
        # Create logger for this port
        serial_logger = RichLogHandler.get_logger(LogSource.SERIAL, port)
        
        # Create monitor command based on mode
        if self.use_fake_monitor:
            command = self._create_fake_monitor_command(port)
        else:
            command = self._create_real_monitor_command(port)
            
        # Create ShellCommandConfig
        config = ShellCommandConfig(
            name=f"Monitor {port}",
            command=command
        )
        
        # Create ShellCommandProcess
        process = ShellCommandProcess(config=config, logger=serial_logger)
        
        # Store process
        self.active_monitors[port] = process
        
        # Update button state
        self._update_button_state(port, True)
        
        # Start process asynchronously
        # Note: This will be handled by the GUI's run_worker
        return True
        
    def _create_fake_monitor_command(self, port: str) -> str:
        """
        Create fake monitor command for testing.
        
        Args:
            port: Port identifier
            
        Returns:
            Command string for fake monitor
        """
        script_path = os.path.join(os.path.dirname(__file__), 'fake_monitor_script.py')
        return f"python3 {script_path} {port}"
        
    def _create_real_monitor_command(self, port: str) -> str:
        """
        Create real serial monitor command using idf.py monitor.
        
        Args:
            port: Port identifier
            
        Returns:
            Command string for real serial monitor
        """
        return f"bash -c 'source {self.idf_setup_path} && idf.py -p /dev/{port} monitor'"
        
    def is_real_port_available(self, port: str) -> bool:
        """
        Check if real serial port is available.
        
        Args:
            port: Port identifier to check
            
        Returns:
            True if port exists and is accessible, False otherwise
        """
        port_path = f"/dev/{port}"
        return os.path.exists(port_path) and os.access(port_path, os.R_OK | os.W_OK)
        
    def get_available_ports(self) -> list[str]:
        """
        Get list of available serial ports.
        
        Returns:
            List of available port identifiers
        """
        ports = []
        
        # Check for ttyACM* ports (USB CDC)
        for port in glob.glob('/dev/ttyACM*'):
            port_name = port[5:]  # Remove '/dev/' prefix
            if self.is_real_port_available(port_name):
                ports.append(port_name)
                
        # Check for ttyUSB* ports (USB-to-serial adapters)
        for port in glob.glob('/dev/ttyUSB*'):
            port_name = port[5:]  # Remove '/dev/' prefix
            if self.is_real_port_available(port_name):
                ports.append(port_name)
                
        return sorted(ports)
        
    def stop_monitor(self, port: str) -> bool:
        """
        Stop monitoring on specific port.
        
        Args:
            port: Port identifier to stop monitoring
            
        Returns:
            True if monitor was stopped, False if not found
        """
        if port not in self.active_monitors:
            return False
            
        process = self.active_monitors[port]
        
        # Terminate the process
        process.terminate()
        
        # Remove from active monitors
        del self.active_monitors[port]
        
        # Update button state
        self._update_button_state(port, False)
        
        return True
        
    def is_monitoring(self, port: str) -> bool:
        """
        Check if port is being monitored.
        
        Args:
            port: Port identifier to check
            
        Returns:
            True if port is being monitored, False otherwise
        """
        return port in self.active_monitors
        
    def get_monitor_process(self, port: str) -> Optional[ShellCommandProcess]:
        """
        Get monitor process for specific port.
        
        Args:
            port: Port identifier
            
        Returns:
            ShellCommandProcess instance or None if not found
        """
        return self.active_monitors.get(port)
        
    def stop_all_monitors(self) -> None:
        """Stop all active monitoring processes."""
        for port in list(self.active_monitors.keys()):
            self.stop_monitor(port)
            
    def _update_button_state(self, port: str, is_monitoring: bool) -> None:
        """
        Update button appearance based on monitoring state.
        
        Args:
            port: Port identifier
            is_monitoring: True if monitoring is active, False otherwise
        """
        button = self.monitor_buttons.get(port)
        if not button:
            return
            
        if is_monitoring:
            # Monitor is ON - show stop button
            button.label = f" 🗙 👁  Stop {port}"
            button.classes = "monitor-button active"
        else:
            # Monitor is OFF - show start button
            button.label = f"  👁  Monitor {port}"
            button.classes = "monitor-button"
            
        # Force button refresh
        button.refresh()
        
    async def run_monitor_with_cleanup(self, port: str) -> bool:
        """
        Run monitor process and handle cleanup when it finishes.
        This method should be called from GUI's run_worker.
        
        Args:
            port: Port identifier
            
        Returns:
            True if monitor completed successfully, False otherwise
        """
        if port not in self.active_monitors:
            return False
            
        process = self.active_monitors[port]
        serial_logger = RichLogHandler.get_logger(LogSource.SERIAL, port)
        

        try:
            serial_logger.info(f"--- Monitor on port {port} starts 🚀 ---") 

            # Run the process and wait for completion
            success = await process.run_end_wait()
            
            # Process finished - update button state
            self._update_button_state(port, False)
            
            # Remove from active monitors
            if port in self.active_monitors:
                del self.active_monitors[port]
                
            if success:
                serial_logger.info(f"=== Monitor on port {port} completed successfully ✅ ===")
            else:
                serial_logger.warning(f"!!! Monitor on port {port} finished with errors ❌ !!!" )
                
            return success
            
        except Exception as e:
            # Process failed with exception
            serial_logger.error(f"Monitor on port {port} failed: {e}")
            
            # Update button state
            self._update_button_state(port, False)
            
            # Remove from active monitors
            if port in self.active_monitors:
                del self.active_monitors[port]
                
            return False