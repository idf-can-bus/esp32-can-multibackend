#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''
Test compilation script for all valid Kconfig combinations.
Tests all meaningful library/example combinations from Kconfig.projbuild
by creating workspaces, configuring sdkconfig, and compiling with ESP-IDF.
Generates comprehensive compilation statistics.
'''

import argparse
import asyncio
import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Tuple, Dict
import traceback

# Import our modules
from py.app_logic import FlashApp
from py.config.kconfig_options import ConfigOption
from py.shell_commands import ShellCommandConfig, ShellCommandProcess


# Setup simple console logger
def setup_console_logger(verbose: bool = False):
    """Setup standard Python logger with console output."""
    logger = logging.getLogger('test_compilation')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Remove any existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


# Global logger (will be initialized in main)
test_logger = None


class SimpleStreamLogger:
    """Simple logger wrapper for ShellCommandProcess that outputs to console."""
    def __init__(self, logger):
        self._logger = logger
        
    def info(self, message):
        """Log info message to console."""
        # Strip Rich markup tags if present
        import re
        clean_msg = re.sub(r'\[/?[a-z\s]+\]', '', message)
        self._logger.info(clean_msg)
        sys.stdout.flush()
        
    def error(self, message):
        """Log error message to console."""
        import re
        clean_msg = re.sub(r'\[/?[a-z\s]+\]', '', message)
        self._logger.error(clean_msg)
        sys.stdout.flush()
        
    def debug(self, message):
        """Log debug message to console."""
        import re
        clean_msg = re.sub(r'\[/?[a-z\s]+\]', '', message)
        self._logger.debug(clean_msg)
        sys.stdout.flush()


class CompilationResult:
    """Container for single compilation test result."""
    def __init__(self, lib_id: str, lib_name: str, example_id: str, example_name: str):
        self.lib_id = lib_id
        self.lib_name = lib_name
        self.example_id = example_id
        self.example_name = example_name
        self.success = False
        self.duration = 0.0
        self.error_message = ""
        self.workspace_path = ""
        self.log_file = ""


class CompilationTester:
    """
    Automated compilation tester for all valid Kconfig combinations.
    Manages workspace creation, compilation, and result logging.
    """

    def __init__(
            self,
            idf_setup_path: str = "~/esp/v5.4.1/esp-idf/export.sh",
            kconfig_path: str = "./main/Kconfig.projbuild",
            sdkconfig_path: str = "./sdkconfig",
            menu_name: str = "*** CAN bus examples  ***",
            fail_fast: bool = False,
    ):
        """
        Initialize compilation tester.
        
        Args:
            idf_setup_path: Path to ESP-IDF environment setup script
            kconfig_path: Path to Kconfig.projbuild file
            sdkconfig_path: Path to sdkconfig file
            menu_name: Menu name in Kconfig to parse
            fail_fast: Stop at first compilation failure
        """
        self.idf_setup_path = os.path.expanduser(idf_setup_path)
        self.kconfig_path = kconfig_path
        self.sdkconfig_path = sdkconfig_path
        self.menu_name = menu_name
        self.fail_fast = fail_fast
        
        # Initialize FlashApp to reuse its logic
        self.flash_app = FlashApp(
            idf_setup_path=idf_setup_path,
            kconfig_path=kconfig_path,
            sdkconfig_path=sdkconfig_path,
            menu_name=menu_name
        )
        
        self.results: List[CompilationResult] = []

    def get_all_valid_combinations(self) -> List[Tuple[ConfigOption, ConfigOption]]:
        """
        Get all valid lib/example combinations based on dependencies.
        
        Returns:
            List of tuples (lib_option, example_option)
        """
        valid_combinations = []
        
        lib_options = self.flash_app.lib_options
        example_options = self.flash_app.example_options
        
        test_logger.info(f"Found {len(lib_options)} libraries and {len(example_options)} examples")
        
        for lib_option in lib_options:
            for example_option in example_options:
                # Check dependencies
                if self.flash_app.check_dependencies(lib_option.id, example_option.id):
                    valid_combinations.append((lib_option, example_option))
                    test_logger.info(
                        f"✓ Valid combination: {lib_option.display_name} + {example_option.display_name}"
                    )
                else:
                    test_logger.debug(
                        f"✗ Invalid combination (dependencies): {lib_option.display_name} + {example_option.display_name}"
                    )
        
        return valid_combinations

    async def compile_combination(
            self, 
            lib_option: ConfigOption, 
            example_option: ConfigOption,
            fullclean: bool = False
    ) -> CompilationResult:
        """
        Compile single lib/example combination.
        
        Args:
            lib_option: Library configuration option
            example_option: Example configuration option
            fullclean: Whether to run fullclean before build
            
        Returns:
            CompilationResult with test outcome
        """
        result = CompilationResult(
            lib_id=lib_option.id,
            lib_name=lib_option.display_name,
            example_id=example_option.id,
            example_name=example_option.display_name
        )
        
        start_time = time.time()
        
        try:
            test_logger.info(f"\n{'='*80}")
            test_logger.info(f"Testing: {lib_option.display_name} + {example_option.display_name}")
            test_logger.info(f"{'='*80}\n")
            
            # Step 1: Switch to workspace
            test_logger.info(f"Step 1: Creating workspace...")
            success_workspace = self.flash_app._switch_to_workspace(
                lib_option.id, 
                example_option.id
            )
            if not success_workspace:
                result.error_message = "Failed to create workspace"
                test_logger.error("❌ Failed to create workspace")
                return result
            
            result.workspace_path = self.flash_app._workspace_path
            test_logger.info(f"✓ Workspace: {result.workspace_path}")
            
            # Step 2: Update sdkconfig
            test_logger.info(f"Step 2: Updating sdkconfig...")
            success_config = self.flash_app._update_sdkconfig(
                lib_option.id, 
                example_option.id
            )
            if not success_config:
                result.error_message = "Failed to update sdkconfig"
                test_logger.error("❌ Failed to update sdkconfig")
                return result
            
            test_logger.info(f"✓ sdkconfig updated")
            
            # Step 3: Compile
            test_logger.info(f"Step 3: Compiling (this may take a while)...")
            jobs = FlashApp.get_optimal_jobs()
            test_logger.info(f"Using {jobs} parallel jobs")
            
            # Build command
            if fullclean:
                command = (
                    f"bash -c 'export MAKEFLAGS=-j{jobs} && "
                    f"source {self.idf_setup_path} && "
                    f"cd {self.flash_app._workspace_path} && "
                    f"idf.py fullclean && idf.py build'"
                )
            else:
                command = (
                    f"bash -c 'export MAKEFLAGS=-j{jobs} && "
                    f"source {self.idf_setup_path} && "
                    f"cd {self.flash_app._workspace_path} && "
                    f"idf.py build'"
                )
            
            # Create log file path
            log_dir = os.path.join(self.flash_app._workspace_path, "test_logs")
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"build_{timestamp}.log")
            result.log_file = log_file
            
            # Execute compilation
            config = ShellCommandConfig(
                name=f"Compile {lib_option.display_name} + {example_option.display_name}",
                command=command
            )
            
            # Use simple logger for process output
            simple_logger = SimpleStreamLogger(test_logger)
            process = ShellCommandProcess(config=config, logger=simple_logger)
            success_compile = await process.run_end_wait()
            
            # Save logs to file
            with open(log_file, 'w') as f:
                f.write(f"Compilation test: {lib_option.display_name} + {example_option.display_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Command: {command}\n")
                f.write(f"{'='*80}\n\n")
                f.write("=== STDOUT ===\n")
                for line in process.stdout_lines:
                    f.write(line + "\n")
                f.write("\n=== STDERR ===\n")
                for line in process.stderr_lines:
                    f.write(line + "\n")
                f.write(f"\n{'='*80}\n")
                f.write(f"Result: {'SUCCESS' if success_compile else 'FAILED'}\n")
            
            result.success = success_compile
            if success_compile:
                test_logger.info(f"✅ Compilation SUCCESSFUL")
            else:
                result.error_message = "Compilation failed (see log file)"
                test_logger.error(f"❌ Compilation FAILED")
                test_logger.error(f"   Log file: {log_file}")
            
        except Exception as e:
            result.error_message = f"Exception: {str(e)}"
            test_logger.error(f"❌ Exception during compilation: {e}")
            test_logger.error(traceback.format_exc())
        
        finally:
            result.duration = time.time() - start_time
            test_logger.info(f"Duration: {result.duration:.1f}s")
        
        return result

    async def run_all_tests(self, fullclean: bool = False) -> None:
        """
        Run compilation tests for all valid combinations.
        
        Args:
            fullclean: Whether to run fullclean before each build
        """
        test_logger.info("=" * 80)
        test_logger.info("Starting compilation tests for all valid configurations")
        test_logger.info("=" * 80)
        
        # Get all valid combinations
        combinations = self.get_all_valid_combinations()
        
        if not combinations:
            test_logger.error("No valid combinations found!")
            return
        
        test_logger.info(f"\nFound {len(combinations)} valid combinations to test")
        if self.fail_fast:
            test_logger.info("Fail-fast mode: will stop at first failure\n")
        else:
            test_logger.info("")
        
        # Test each combination
        for idx, (lib_option, example_option) in enumerate(combinations, 1):
            test_logger.info(f"\n[{idx}/{len(combinations)}] Testing combination...")
            result = await self.compile_combination(lib_option, example_option, fullclean)
            self.results.append(result)
            
            # Check fail-fast mode
            if self.fail_fast and not result.success:
                test_logger.warning(f"\n⚠️  Fail-fast mode: stopping at first failure")
                break
        
        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print comprehensive test results summary."""
        test_logger.info("\n" + "=" * 80)
        test_logger.info("COMPILATION TEST SUMMARY")
        test_logger.info("=" * 80 + "\n")
        
        # Count successes and failures
        successes = [r for r in self.results if r.success]
        failures = [r for r in self.results if not r.success]
        
        # Print successful builds
        if successes:
            test_logger.info(f"✅ SUCCESSFUL BUILDS ({len(successes)}):")
            test_logger.info("-" * 80)
            for result in successes:
                test_logger.info(
                    f"  ✓ {result.lib_name:30s} + {result.example_name:30s} "
                    f"({result.duration:.1f}s)"
                )
            test_logger.info("")
        
        # Print failed builds
        if failures:
            test_logger.info(f"❌ FAILED BUILDS ({len(failures)}):")
            test_logger.info("-" * 80)
            for result in failures:
                test_logger.info(
                    f"  ✗ {result.lib_name:30s} + {result.example_name:30s}"
                )
                test_logger.info(f"    Error: {result.error_message}")
                test_logger.info(f"    Workspace: {result.workspace_path}")
                test_logger.info(f"    Log file: {result.log_file}")
                test_logger.info("")
        
        # Print statistics
        test_logger.info("=" * 80)
        test_logger.info("STATISTICS:")
        test_logger.info("-" * 80)
        total = len(self.results)
        success_count = len(successes)
        failure_count = len(failures)
        success_rate = (success_count / total * 100) if total > 0 else 0
        total_time = sum(r.duration for r in self.results)
        
        test_logger.info(f"  Total combinations tested: {total}")
        test_logger.info(f"  Successful builds:         {success_count}")
        test_logger.info(f"  Failed builds:             {failure_count}")
        test_logger.info(f"  Success rate:              {success_rate:.1f}%")
        test_logger.info(f"  Total compilation time:    {total_time:.1f}s ({total_time/60:.1f} min)")
        if total > 0:
            avg_time = total_time / total
            test_logger.info(f"  Average time per build:    {avg_time:.1f}s")
        test_logger.info("=" * 80)
        
        # Final verdict
        if failure_count == 0:
            test_logger.info("\n🎉 ALL TESTS PASSED! 🎉\n")
        else:
            test_logger.info(f"\n⚠️  {failure_count} TEST(S) FAILED ⚠️\n")


async def main():
    """Main entry point for compilation tester."""
    global test_logger
    
    parser = argparse.ArgumentParser(
        description="Test compilation of all valid Kconfig combinations"
    )
    parser.add_argument(
        '-k', '--kconfig',
        default="./main/Kconfig.projbuild",
        help="Path to Kconfig file (default: ./main/Kconfig.projbuild)"
    )
    parser.add_argument(
        '-s', '--sdkconfig',
        default="./sdkconfig",
        help="Path to sdkconfig file (default: ./sdkconfig)"
    )
    parser.add_argument(
        '-i', '--idf_setup',
        default="~/esp/v5.4.1/esp-idf/export.sh",
        help="Path to ESP-IDF setup script (default: ~/esp/v5.4.1/esp-idf/export.sh)"
    )
    parser.add_argument(
        '-f', '--fullclean',
        action='store_true',
        help="Run fullclean before each build"
    )
    parser.add_argument(
        '-1', '--fail-fast',
        action='store_true',
        help="Stop at first compilation failure"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup console logger
    test_logger = setup_console_logger(verbose=args.verbose)
    
    test_logger.info("ESP32 Compilation Test Tool")
    test_logger.info(f"Kconfig: {args.kconfig}")
    test_logger.info(f"IDF Setup: {args.idf_setup}")
    test_logger.info("")

    # Create tester instance
    tester = CompilationTester(
        idf_setup_path=args.idf_setup,
        kconfig_path=args.kconfig,
        sdkconfig_path=args.sdkconfig,
        fail_fast=args.fail_fast,
    )

    # Run all tests
    await tester.run_all_tests(fullclean=args.fullclean)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        if test_logger:
            test_logger.info("\n\n⚠️  Tests interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        if test_logger:
            test_logger.error(f"\n\n❌ Fatal error: {e}\n")
            test_logger.error(traceback.format_exc())
        else:
            print(f"Fatal error: {e}", file=sys.stderr)
            traceback.print_exc()
        sys.exit(1)