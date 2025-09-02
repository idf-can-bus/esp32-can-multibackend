#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Fake monitor logic for testing monitor start/stop functionality.
Generates simulated serial output without real hardware.
Inherits from BaseMonitorLogic for common functionality.
'''

import logging
import threading
import time
import random

from py.monitor.base_monitor_logic import BaseMonitorLogic
from py.log.rich_log_handler import LogSource, RichLogHandler


class FakeMonitorLogic(BaseMonitorLogic):
    """
    Fake monitor logic for testing monitor start/stop functionality.
    Generates simulated serial output without real hardware.
    Inherits common functionality from BaseMonitorLogic.
    """

    def _run_monitor(self, port: str, stop_event: threading.Event) -> None:
        """
        Internal method to run fake monitor with custom log format.
        Generates simulated ESP32 boot sequence and continuous CAN messages.
        
        Args:
            port: Port identifier being monitored
            serial_logger: Logger instance for output
            stop_event: Event to check for stop signal
        """
        serial_logger = RichLogHandler.get_logger(LogSource.FAKE_SERIAL, port)
        try:

            # Generate initial connection message
            serial_logger.info(f"[FAKE] Connected to /dev/{port} at 115200 baud")
            serial_logger.info(f"[FAKE] ESP32 boot sequence started...")

            # Simulate boot messages
            boot_messages = [
                "(1234) cpu_start: Starting scheduler.",
                "(1235) heap_init: Initializing. RAM available for dynamic allocation:",
                "(1236) heap_init: At 3FFAE6E0 len 00001920 (6 KiB): DRAM",
                "(1237) heap_init: At 3FFB2EC8 len 0002D138 (180 KiB): DRAM",
                "(1238) heap_init: At 3FFE0440 len 00003BC0 (15 KiB): D/IRAM",
                "(1239) heap_init: At 3FFE4350 len 0001BCB0 (111 KiB): D/IRAM",
                "(1240) heap_init: At 4008044C len 0001FBB4 (127 KiB): IRAM",
                "(1241) heap_init: At 40090000 len 00010000 (64 KiB): Cache",
                "(1242) boot: ESP-IDF v5.4.1 2nd stage bootloader",
                "(1243) boot: compile time 12:34:56",
                "(1244) boot: chip revision: v1.0",
                "(1245) boot: min chip revision: v0.0",
                "(1246) boot: flash size: 4MB",
                "(1247) boot: flash mode: DIO",
                "(1248) boot: flash freq: 80MHz",
                "(1249) boot: flash crypt: 0",
                "(1250) boot: secure boot: 0",
                "(1251) boot: flash verification: 0",
                "(1252) boot: flash encryption: 0",
                "(1253) boot: flash secure: 0",
                "(1254) boot: flash app offset: 0x10000",
                "(1255) boot: flash app size: 0x100000",
                "(1256) boot: flash app hash: 0x12345678",
                "(1257) boot: flash app valid: 1",
                "(1258) boot: flash app verified: 1",
                "(1259) boot: flash app loaded: 1",
                "(1260) boot: Starting app...",
                "(1261) app_main: Starting CAN bus application...",
                "(1262) can: CAN driver initialized",
                "(1263) can: CAN bus started",
                "(1264) can: CAN message received: ID=0x123, DLC=8, Data=[01 02 03 04 05 06 07 08]",
                "(1265) can: CAN message sent: ID=0x456, DLC=4, Data=[AA BB CC DD]",
            ]

            # Send boot messages
            for message in boot_messages:
                if stop_event.is_set():
                    break
                serial_logger.info(f"[FAKE] {message}")
                time.sleep(0.1)  # Simulate real-time output

            # Continuous fake output loop
            message_counter = 1266
            while not stop_event.is_set():
                # Generate random CAN messages
                can_id = random.randint(0x100, 0x7FF)
                dlc = random.randint(1, 8)
                data = [random.randint(0, 255) for _ in range(dlc)]
                data_hex = ' '.join([f"{b:02X}" for b in data])

                message = f"can: CAN message received: ID=0x{can_id:03X}, DLC={dlc}, Data=[{data_hex}]"
                serial_logger.info(f"[FAKE] ({message_counter}) {message}")

                message_counter += 1
                time.sleep(2)  # Generate message every 2 seconds

                # Occasionally generate error messages
                if random.random() < 0.1:  # 10% chance
                    error_msg = f"can: CAN bus error detected: {random.choice(['bit error', 'stuff error', 'form error', 'ack error'])}"
                    serial_logger.warning(f"[FAKE] ({message_counter}) {error_msg}")
                    message_counter += 1
                        
        except Exception as e:
            serial_logger.error(f"❌ [FAKE] Monitor on port {port} failed with exception: {e}")
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
            String identifier for the fake monitor type
        """
        return "FAKE"
