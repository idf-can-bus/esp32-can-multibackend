#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
GUI logic for managing monitor buttons and their states.
Handles button updates, state synchronization, and visual feedback.
'''

import logging
from typing import Dict, Optional
from textual.widgets import Button

logger = logging.getLogger(__name__)

class MonitorGuiLogic:
    """
    GUI logic for managing monitor buttons and their states.
    Handles button updates, state synchronization, and visual feedback.
    """

    def __init__(self):
        # Cache of monitor buttons - key: port, value: Button widget
        self.monitor_buttons: Dict[str, Button] = {}
        # Current monitoring states - key: port, value: bool (True = monitoring)
        self.monitoring_states: Dict[str, bool] = {}

    def register_monitor_button(self, port: str, button: Button) -> None:
        """
        Register a monitor button for a specific port.
        
        Args:
            port: Port identifier
            button: Button widget to manage
        """
        self.monitor_buttons[port] = button
        self.monitoring_states[port] = False
        self._update_button_appearance(port, False)

    def set_monitor_state(self, port: str, is_monitoring: bool) -> None:
        """
        Set monitoring state for a specific port and update button appearance.
        
        Args:
            port: Port identifier
            is_monitoring: True if monitoring is active, False otherwise
        """
        if port in self.monitor_buttons:
            self.monitoring_states[port] = is_monitoring
            self._update_button_appearance(port, is_monitoring)
            logger.debug(f"Monitor state for {port}: {'ON' if is_monitoring else 'OFF'}")
        else:
            logger.warning(f"Monitor button for port {port} not registered")

    def set_all_monitors_off(self) -> None:
        """Turn off all monitors and update all button states."""
        for port in self.monitor_buttons.keys():
            self.set_monitor_state(port, False)

    def get_monitoring_state(self, port: str) -> bool:
        """
        Get current monitoring state for a port.
        
        Args:
            port: Port identifier
            
        Returns:
            True if monitoring is active, False otherwise
        """
        return self.monitoring_states.get(port, False)

    def get_active_monitor_ports(self) -> list[str]:
        """
        Get list of ports that are currently being monitored.
        
        Returns:
            List of active port identifiers
        """
        return [port for port, state in self.monitoring_states.items() if state]

    def _update_button_appearance(self, port: str, is_monitoring: bool) -> None:
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
            button.label = f" 👁   Monitor {port}"
            button.classes = "monitor-button"

        # Force button refresh
        button.refresh()

    def refresh_all_buttons(self) -> None:
        """Refresh all monitor buttons to ensure visual consistency."""
        for port in self.monitor_buttons.keys():
            state = self.monitoring_states.get(port, False)
            self._update_button_appearance(port, state)