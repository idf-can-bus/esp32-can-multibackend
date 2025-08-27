#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Core business logic for ESP32 flash tool application.
Handles configuration updates, code compilation with ESP-IDF, and firmware upload.
Manages the complete workflow from Kconfig parsing to ESP32 flashing.
'''

import glob
import logging
import re
from typing import List, Optional
import threading

from .commands import ShellCommand,ShellCommandRunner
from py.config.kconfig_options import ConfigOption, KconfigMenuItems
from py.config.sdkconfig_options import Sdkconfig
from py.monitor.fake_monitor_logic import FakeMonitorLogic
from py.monitor.serial_monitor_logic import SerialMonitorLogic
from .log.rich_log_handler import LogSource, RichLogHandler

config_logger = RichLogHandler.get_logger(LogSource.CONFIG)
reconfig_logger = RichLogHandler.get_logger(LogSource.RECONFIG)

class FlashApp(ShellCommandRunner):
    """
    Logic class for ESP32 flash operations
    Handles all business logic separate from GUI
    """

    def __init__(
            self,
            idf_setup_path: str = "~/esp/v5.4.1/esp-idf/export.sh",
            kconfig_path: str = "./main/Kconfig.projbuild",
            sdkconfig_path: str = "./sdkconfig",
            gui_app=None,
            menu_name: str = "*** CAN bus examples  ***"
    ):
        self.idf_setup_path = idf_setup_path
        self.kconfig_path = kconfig_path
        self.sdkconfig_path = sdkconfig_path
        self.menu_name = menu_name
        self.gui_app = gui_app  # Optional reference to GUI
        self.kconfig_dict = None  # Will be initialized in re_init()
        self.sdkconfig = None  # Will be initialized in re_init()
        self.lib_options = []  # List of ConfigOption for libraries, will be initialized in re_init()
        
        # Compilation monitoring attributes
        self.compilation_process = None
        self.compilation_lib_id = None
        self.compilation_example_id = None

        # Monitor logic instance
        # @TODO: Change to FlashMonitorLogic for real monitoring FlashMonitorLogic()
        # self.monitor_logic = SerialMonitorLogic()
        self.monitor_logic = FakeMonitorLogic()
        self.re_init()

    def re_init(self):
        # Load KconfigMenuItems for direct access
        self.kconfig_dict = KconfigMenuItems(self.kconfig_path, self.menu_name)

        # Load sdkconfig
        self.sdkconfig = Sdkconfig(self.sdkconfig_path, self.menu_name)

        # Check for missing CONFIG keys and add them to sdkconfig
        self.sdkconfig.add_no_existing_bool_keys(self.kconfig_dict.get_all_options().keys())

        # # Debug: Print loaded sdkconfig lines
        # print("=== _sdkconfig_lines ===")
        # pprint(self.sdkconfig._sdkconfig_lines)
        # print("=== _keys_to_lines_number ===")
        # pprint(self.sdkconfig._keys_to_lines_number)
        # exit(1)

        # Load configuration options (for backward compatibility)
        self.lib_options, self.example_options = self.load_kconfig_options()

    def get_lib_option_by_id(self, lib_id: str) -> Optional[ConfigOption]:
        """Find lib option by ID using KconfigMenuItems"""
        return self.kconfig_dict.get_option_by_id("Select CAN driver/library", lib_id)

    def get_example_option_by_id(self, example_id: str) -> Optional[ConfigOption]:
        """Find example option by ID using KconfigMenuItems"""
        return self.kconfig_dict.get_option_by_id("Select example", example_id)

    def check_dependencies(self, lib_id: str, example_id: str, prompt_char: str = '✏️') -> bool:
        """Check if selected lib satisfies ALL example dependencies"""
        if not lib_id or not example_id:
            return False

        lib_option = self.get_lib_option_by_id(lib_id)
        example_option = self.get_example_option_by_id(example_id)

        config_logger.debug(f"{prompt_char} lib_id='{lib_id}', lib_option={lib_option}")
        config_logger.debug(f"{prompt_char} example_id='{example_id}', example_option={example_option}")

        if not lib_option or not example_option:
            config_logger.debug(f"{prompt_char} One or both options not found")
            return False

        # If example has no dependencies, it's always compatible
        if not example_option.depends_on:
            config_logger.debug(f"{prompt_char} No dependencies required - compatible")
            return True

        # Check if selected lib ID is in the depends_on list
        if lib_option.id in example_option.depends_on:
            config_logger.debug(f"{prompt_char} {lib_option.id} found in dependencies {example_option.depends_on} -> OK")
            return True
        else:
            config_logger.debug(f"{prompt_char} {lib_option.id} NOT found in dependencies {example_option.depends_on} -> FAIL")
            return False

    def update_sdkconfig(self, lib_id: str, example_id: str ) -> bool:
        """Update sdkconfig using new Sdkconfig classes"""
        try:
            reconfig_logger.info(f"Updating sdkconfig for lib='{lib_id}' and example='{example_id}'")

            # Step 1: Get all config option IDs from KconfigMenuItems
            all_options = self.kconfig_dict.get_all_options()
            config_ids = list(all_options.keys())
            reconfig_logger.debug(f"Found {len(config_ids)} config options: {config_ids}")

            # Step 2: Find relevant SdkconfigLines for these IDs
            relevant_lines = {}
            for config_id in config_ids:
                line = self.sdkconfig.get_line_by_key(config_id)
                if line:
                    relevant_lines[config_id] = line
                    config_logger.debug(f"Found existing line for {config_id}: {line.value}")
                else:
                    config_logger.debug(
                        f"Config {config_id} not found in sdkconfig (should have been added during initialization)")

            # Step 3: Set values based on selections
            changes_made = 0
            for config_id, line in relevant_lines.items():
                new_value = None

                # Determine new value based on selection
                if config_id == lib_id:
                    new_value = 'y'
                    reconfig_logger.info(f"ENABLE: {config_id} (selected lib)")
                elif config_id == example_id:
                    new_value = 'y'
                    reconfig_logger.info(f"ENABLE: {config_id} (selected example)")
                else:
                    new_value = 'n'
                    reconfig_logger.debug(f"DISABLE: {config_id} (not selected)")

                # Update line if value changed
                if line.value != new_value:
                    line.set_value(new_value)
                    changes_made += 1
                    reconfig_logger.debug(f"Changed {config_id}: {line.value} -> {new_value}")

            # Step 4: Write sdkconfig if any changes were made
            if changes_made > 0:
                reconfig_logger.info(f"Writing sdkconfig with {changes_made} changes")
                self.sdkconfig.write()
                reconfig_logger.info(f"Successfully updated sdkconfig")
            else:
                config_logger.info("No changes needed in sdkconfig")

            return True

        except Exception as e:
            config_logger.error(f"Failed to update sdkconfig: {e}")
            import traceback
            config_logger.debug(traceback.format_exc())
            return False

    def _update_config(self, lib_id: str, example_id: str) -> bool:
        """
        Step 1: Update sdkconfig configuration
        Returns True if successful, False otherwise
        """
        return self.update_sdkconfig(lib_id, example_id)

    def config_compile_flash(self, port: str, lib_id: str, example_id: str) -> bool:
        """
        Execute complete flash sequence: update config, compile, upload
        Returns True if all steps successful, False if any step fails
        """
        # Stop all monitors before starting flash operations
        self.stop_all_monitors()
        
        # Step 1: Update sdkconfig
        if not self._update_config(lib_id, example_id):
            config_logger.error("Flash sequence aborted: sdkconfig update failed")
            return False

        list_of_dependig_commands = [
            # Step 2: Compile code
            ShellCommand(
                name="Compile",
                command=f"bash -c 'source {self.idf_setup_path} && idf.py all'",
                logger=RichLogHandler.get_logger(LogSource.BUILD)
            ),
            # Step 3: Flash firmware
            ShellCommand(
                name=f"Flash to port '/dev/{port}'",
                command=f"bash -c 'source {self.idf_setup_path} && idf.py -p /dev/{port} flash'",
                logger=RichLogHandler.get_logger(LogSource.FLASH, f'FLASH to {port}')
            )
        ]

        # Run command in a separate thread to keep UI responsive
        thread = threading.Thread(
            target=self.run_commands,
            args=(list_of_dependig_commands, False)
        )
        thread.start()

        return True

    def stop_all_monitors(self) -> None:
        """Delegate to monitor logic"""
        self.monitor_logic.stop_all_monitors()

    def stop_monitor(self, port: str) -> bool:
        """Delegate to monitor logic"""
        return self.monitor_logic.stop_monitor(port)

    def is_monitoring(self, port: str) -> bool:
        """Delegate to monitor logic"""
        return self.monitor_logic.is_monitoring(port)

    def monitor_port(self, port: str, serial_logger: RichLogHandler) -> None:
        """
        Delegate monitor operation to monitor logic
        """
        self.monitor_logic.start_monitor(port, self.idf_setup_path, serial_logger)

    @staticmethod
    def find_flash_ports(default_ports: list[str] = ['Port1', 'Port2', 'Port3', 'Port4']):
        """Find available flash ports"""
        ports = glob.glob('/dev/ttyACM*')
        flash_ports1 = sorted(p[5:] for p in ports if re.match(r'/dev/ttyACM\d+$', p))
        ports = glob.glob('/dev/ttyUSB*')
        flash_ports2 = sorted(p[5:] for p in ports if re.match(r'/dev/ttyUSB\d+$', p))
        flash_ports = flash_ports1 + flash_ports2
        if not flash_ports:
            return default_ports
        else:
            return flash_ports

    def load_kconfig_options(self) -> tuple[List[ConfigOption], List[ConfigOption]]:
        """Load lib and example options from Kconfig file using KconfigMenuItems"""

        # Extract lib options from "Select CAN driver/library" menu
        lib_menu = "Select CAN driver/library"
        lib_options = []
        if lib_menu in self.kconfig_dict._menus_dict:
            for option in self.kconfig_dict._menus_dict[lib_menu].values():
                # Convert new ConfigOption to old format for compatibility
                lib_options.append(ConfigOption(
                    id=option.id,
                    display_name=option.display_name,
                    config_type=option.config_type,
                    depends_on=option.depends_on
                ))

        # Extract example options from "Select example" menu  
        example_menu = "Select example"
        example_options = []
        if example_menu in self.kconfig_dict._menus_dict:
            for option in self.kconfig_dict._menus_dict[example_menu].values():
                # Convert new ConfigOption to old format for compatibility
                example_options.append(ConfigOption(
                    id=option.id,
                    display_name=option.display_name,
                    config_type=option.config_type,
                    depends_on=option.depends_on
                ))

        return lib_options, example_options 