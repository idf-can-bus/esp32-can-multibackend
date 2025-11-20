# can-multibackend-idf

Multi-Backend CAN Example Suite for ESP-IDF
============================================

This project demonstrates CAN bus communication on ESP-IDF platforms (ESP32, ESP32-S3, ESP32-C3, ESP32-C6) using multiple hardware backends. It provides a collection of working examples that can run on different CAN controllers (built-in TWAI or external MCP25xxx via SPI) with minimal code changes, making it easy to compare different hardware solutions and choose the best fit for your application.

**Note:** This is primarily an **example and demonstration project**. While the included libraries (twai-idf-can, mcp25xxx-multi-idf-can) are production-ready, the `can_dispatch` abstraction layer used here is designed for demonstrating interchangeable backends in single-device examples, not as a general-purpose unified API for production use.

## Architecture Overview

This integration project combines three independent CAN libraries to demonstrate different CAN implementation approaches:

### Core Libraries

1. **[twai-idf-can](https://github.com/idf-can-bus/twai-idf-can)** — High-level wrapper for ESP32's built-in TWAI (CAN) controller with automatic error recovery
   - Direct support for ESP32's native CAN peripheral
   - Simplified configuration and initialization
   - Automatic bus-off recovery

2. **[mcp2515-esp32-idf](https://github.com/Microver-Electronics/mcp2515-esp32-idf)** — External library for single MCP2515 CAN controller via SPI
   - Low-level driver for MCP2515 chip
   - Single-device operation
   - Third-party library by Microver-Electronics

3. **[mcp25xxx-multi-idf-can](https://github.com/idf-can-bus/mcp25xxx-multi-idf-can)** — Multi-device adapter for MCP25xxx family (MCP2515, MCP25625, etc.)
   - Supports multiple MCP25xxx controllers simultaneously
   - Built upon and extends mcp2515-esp32-idf
   - Unified multi-device API

### Shared Components

- **[examples-utils-idf-can](https://github.com/idf-can-bus/examples-utils-idf-can)** — Common utility functions shared across all examples
  - Message formatting and display
  - Timing and synchronization helpers
  - Reusable across all backend types

All repositories are maintained under the **[idf-can-bus](https://github.com/idf-can-bus)** organization on GitHub.

## Understanding CAN Hardware

A complete CAN bus interface requires two hardware components:

### 1. CAN Controller
Implements the CAN protocol at the logic level:
- Creates and decodes CAN frames
- Handles timing, bit stuffing, and arbitration
- Manages error detection and message filtering
- Operates at digital logic level (0/1 signals)

### 2. CAN Transceiver
Provides the physical layer interface:
- Converts logic signals to differential voltage on CANH/CANL lines
- Converts differential signals back to logic levels
- Provides noise immunity and ESD protection
- Common chips: TJA1050, SN65HVD230, MCP2551

### Hardware Options in This Project

**ESP32 with TWAI (built-in):**
- ✅ **CAN Controller** is integrated in ESP32 (TWAI peripheral)
- ⚠️ **CAN Transceiver** still required externally (e.g., SN65HVD230, TJA1050)

**MCP2515 (external via SPI):**
- ✅ **CAN Controller** is the MCP2515 chip
- ⚠️ **CAN Transceiver** still required externally (e.g., MCP2551)

**MCP25625 (integrated solution):**
- ✅ **CAN Controller + Transceiver** in one chip (MCP25625 = MCP2515 + MCP2551)
- ✅ No additional transceiver needed

## Features

- **Multiple Backend Support:** Compare TWAI (built-in) vs MCP25xxx (external SPI) implementations
- **Interchangeable Examples:** Same example code runs on different backends via Kconfig selection
- **Backend Abstraction Layer:** `can_dispatch` provides `can_twai_*` interface for single-device examples (demonstration purposes)
- **Single and Multi-Device Examples:** From simple single-bus scenarios to complex multi-bus setups (MCP25xxx only)
- **Easy Configuration:** Select backend and example via `idf.py menuconfig`
- **Development Tools:** Python-based flash manager with GUI for multi-device workflows
- **Automatic Testing:** `test_compilation.py` validates all backend/example combinations

## Supported Hardware Configurations

| Configuration | Backend Library | CAN Controller | CAN Transceiver | Use Case |
|---------------|----------------|----------------|-----------------|----------|
| **TWAI** | [twai-idf-can](https://github.com/idf-can-bus/twai-idf-can) | ESP32 built-in TWAI | External (SN65HVD230, TJA1050) | Best performance, lowest cost, single bus |
| **MCP2515 Single** | [mcp2515-esp32-idf](https://github.com/Microver-Electronics/mcp2515-esp32-idf) (via `can_dispatch`) | MCP2515 via SPI | External (MCP2551) or integrated (MCP25625) | Flexible GPIO, single device |
| **MCP25xxx Multi** | [mcp25xxx-multi-idf-can](https://github.com/idf-can-bus/mcp25xxx-multi-idf-can) | Multiple MCP2515/25625 via SPI | External or integrated | Multiple independent CAN buses |

## Example Applications

This project provides **12 example configurations** demonstrating the same functionality across different hardware backends. The examples combine 3 application types (send, receive_poll, receive_interrupt) with 4 backend configurations.

**Key Concept:** Single-device examples use identical code across all backends (TWAI, MCP2515, MCP25xxx) thanks to the `can_dispatch` abstraction layer. This allows direct comparison of different hardware solutions with the same application logic.

Examples are organized by device count (single/multi) and maintained in their respective component repositories:

| Library/HW | | **Single Device** | | | **Multi Device** | |
|------------|---------|-------------------|---------|---------|------------------|---------|
| | **send** | **receive_poll** | **receive_interrupt** | **send** | **receive_poll** | **receive_interrupt** |
| **TWAI**<br>(ESP32 built-in CAN) | ✅ | ✅ | ✅ | — | — | — |
| **MCP2515 Single**<br>(External via SPI) | ✅ | ✅ | ✅ | — | — | — |
| **MCP25xxx Multi**<br>(Multiple devices via SPI) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Notes:**
- **Single-device examples** use `can_twai_*` API (abstracted via `can_dispatch` for demonstration purposes)
  - Same example code runs on TWAI, MCP2515, or MCP25xxx backends
  - Backend selection via Kconfig at compile time
  - `can_dispatch` is a thin wrapper for examples, not recommended as production API
- **Multi-device examples** use native `canif_*` API from mcp25xxx-multi-idf-can library
  - Only available for MCP25xxx backend (ESP32 has only one built-in TWAI controller)
  - Production-ready API designed for multiple independent CAN buses
- **MCP25xxx Multi (single mode)** demonstrates using the multi-device library with `device_count = 1`
- All examples share common utilities from `examples-utils-idf-can` submodule

### Example Locations

**Single Device (TWAI & MCP2515):**
- Source: [`components/twai-idf-can/examples/`](https://github.com/idf-can-bus/twai-idf-can/tree/master/examples)
- API: `can_twai_*` functions
- Backends: Selectable via Kconfig (TWAI or MCP2515 single)

**Multi Device (MCP25xxx):**
- Source: [`components/mcp25xxx-multi-idf-can/examples/`](https://github.com/idf-can-bus/mcp25xxx-multi-idf-can/tree/master/examples)
- API: `canif_*` functions
- Backend: Multiple MCP25xxx controllers

For detailed usage and API documentation, see the respective library repositories linked above.

For local navigation, see [`examples/README.md`](examples/README.md)

## Hardware Wiring

### Typical MCP2515 Setup

![Single MCP2515 wiring](doc/single_setup.wiring.drawio.png)

*Diagram shows MCP2515 CAN controller connected via SPI, with separate MCP2551 CAN transceiver for the physical layer. See [Understanding CAN Hardware](#understanding-can-hardware) section for component details.*

**Important notes:**
- **CAN bus termination:** The general recommendation is to place one 120-ohm termination resistor at each end of a long CAN bus. However, the author's experience with short experimental setups shows that using only one 120-ohm resistor for the entire bus often works better.
- **GPIO configuration:** Custom GPIO assignments are fully configurable (see example configuration files)
- **SPI buses:** Either SPI2_HOST or SPI3_HOST can be used on ESP32 (SPI1_HOST is reserved for flash)
- **Multiple devices:** Multiple MCP25xxx devices can share the same SPI bus (MISO/MOSI/SCK), each with unique CS pin
- **TWAI wiring:** For ESP32 built-in TWAI connections, see [twai-idf-can documentation](https://github.com/idf-can-bus/twai-idf-can)

## Building and Flashing

### Prerequisites

Before building, ensure ESP-IDF is properly installed and activated:

```sh
# Activate ESP-IDF environment
. $HOME/esp/esp-idf/export.sh  # Adjust path to your ESP-IDF installation

# Initialize and update all submodules (including nested ones)
git submodule update --init --recursive
```

### Method 1: Using ESP-IDF Command Line (Traditional)

Traditional ESP-IDF workflow using a single `build/` directory:

```sh
# Configure backend and example
idf.py menuconfig   # Navigate to "CAN Backend" and "Example Selection"

# Build and flash
idf.py build        # Builds to ./build/ directory
idf.py -p /dev/ttyACM0 flash monitor
```

**Note:** When switching configurations via menuconfig, a full rebuild is required. For multi-configuration development, consider using Methods 2 or 3 with isolated workspaces (see [Understanding Build Workspaces](#understanding-build-workspaces)).

### Method 2: Using Python Flash Manager (Recommended for Multi-Configuration)

The `flash_manager.py` tool provides a comprehensive Textual-based GUI for managing ESP32 development workflows. It uses isolated build workspaces (see [Understanding Build Workspaces](#understanding-build-workspaces)), allowing instant switching between configurations without rebuilding. Ideal for projects with multiple ESP32 boards requiring different backend/example combinations.

**Launch the Flash Manager:**

```sh
python3 flash_manager.py
```

#### Build & Flash Tab
![Build and flash tab](doc/build_flash.png)

The **Build & Flash** tab streamlines firmware deployment:
- Auto-detects connected ESP32 devices (ttyACM*, ttyUSB*)
- Select CAN backend (TWAI, MCP2515 single/multi) and example application per device
- Validates configuration dependencies automatically
- Manages isolated build workspaces for each backend/example combination
  - Builds are stored in `.workspaces/` subdirectories
  - Directory names derived from configuration combination (e.g., `CAN_BACKEND_MCP2515_SINGLE_EXAMPLE_RECV_INT_SINGLE`)
  - No rebuild needed when switching between configurations
  - Can flash manually from workspace directories: `cd .workspaces/<config_name> && idf.py -p <port> flash`
- Displays real-time compilation output with color-coded logging
- Handles complete workflow: configuration → build → flash in one click
- Uses optimal parallel jobs based on available CPU and memory

#### Serial Monitors Tab
![Monitor tab](doc/serial_monitors.png)

The **Serial Monitors** tab enables real-time device monitoring:
- Open multiple serial monitors simultaneously for connected devices
- Real-time output streaming with configurable buffering
- Start/Stop individual monitors without affecting others
- Hide/Show monitor logs while keeping background logging active
- Automatic port detection and fake ports for testing
- Character-by-character or buffered output display
- Supports monitoring alongside build operations

### Method 3: Automated Compilation Testing

Validate all backend/example combinations:

```sh
python3 test_compilation.py
```

This script:
- Tests all 12 possible configurations (3 example types × 4 backend configurations)
- Uses the same `.workspaces/` directory structure as `flash_manager.py`
- Creates isolated build directories for each configuration combination
- Generates detailed compilation logs in `<workspace>/test_logs/` subdirectories
- Provides comprehensive statistics at the end (success rate, timing, errors)

### Understanding Build Workspaces

This project supports two distinct build strategies:

#### Strategy 1: Single Build Directory (Method 1)
**Traditional ESP-IDF approach:**
- Uses `idf.py menuconfig` to configure backend and example
- Builds into a single `./build/` directory
- **Requires full rebuild** when switching between configurations via menuconfig
- Suitable for working on a single configuration

```sh
idf.py menuconfig    # Select configuration
idf.py build         # Builds to ./build/
idf.py -p <port> flash
```

#### Strategy 2: Isolated Workspaces (Methods 2 & 3)
**Multi-configuration approach:**
- Each backend/example combination gets its own workspace directory
- Workspace path: `.workspaces/<CAN_BACKEND>_<EXAMPLE>/`
- Example: `.workspaces/CAN_BACKEND_MCP2515_SINGLE_EXAMPLE_RECV_INT_SINGLE/`
- **No rebuild needed** when switching between configurations
- Ideal for testing multiple configurations or multi-device development

**Using isolated workspaces:**

```sh
# Option A: Use flash_manager.py GUI
python3 flash_manager.py

# Option B: Use test_compilation.py for batch testing
python3 test_compilation.py

# Option C: Manual build and flash from workspace
cd .workspaces/CAN_BACKEND_MCP2515_SINGLE_EXAMPLE_RECV_INT_SINGLE
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

**Benefits of isolated workspaces:**
- Switch between configurations instantly without rebuilding
- Parallel development on multiple configurations
- Preserve build artifacts for all tested combinations
- Efficient CI/CD testing (test_compilation.py can validate all 12 combinations)
- Multiple developers can work on different configurations without conflicts

## Project Structure

```
can-multibackend-idf/
├── components/          # CAN backend libraries (git submodules)
│   ├── twai-idf-can/             # TWAI wrapper with examples
│   ├── mcp2515-esp32-idf/        # External MCP2515 single library
│   ├── mcp25xxx-multi-idf-can/   # MCP25xxx multi-device with examples
│   └── can_dispatch/             # Backend abstraction layer
├── examples/            # Example documentation and references
├── main/                # Project entry point and Kconfig configuration
├── py/                  # Python flash manager (GUI and backend logic)
├── doc/                 # Documentation and wiring diagrams
├── .workspaces/         # Isolated build workspaces (Methods 2 & 3)
│   ├── CAN_BACKEND_TWAI_EXAMPLE_SEND_SINGLE/
│   ├── CAN_BACKEND_MCP2515_SINGLE_EXAMPLE_RECV_INT_SINGLE/
│   └── ... (one directory per configuration combination)
├── build/               # Traditional build directory (Method 1)
├── flash_manager.py     # Python GUI for multi-device management
├── test_compilation.py  # Automated build testing script
└── CMakeLists.txt       # Main project CMake configuration
```

### Key Components

- **`can_dispatch/`** — Thin abstraction layer providing `can_twai_*` API for single-device examples
  - Maps calls to the selected backend (TWAI or MCP2515) via Kconfig
  - Designed for demonstration and comparison purposes
  - Not intended as a general-purpose production API
- **Submodules** — Each CAN library is a git submodule with its own repository
  - Production-ready libraries: `twai-idf-can` and `mcp25xxx-multi-idf-can`
  - Third-party library: `mcp2515-esp32-idf` (Microver Electronics)
- **Nested Submodules** — Both `twai-idf-can` and `mcp25xxx-multi-idf-can` include `examples-utils-idf-can` as a nested submodule

## License
MIT License — see [LICENSE](LICENSE)

---

*Author: Ivo Marvan, 2025*
