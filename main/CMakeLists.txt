# Select example source based on Kconfig
# Examples are compiled from their component directories using can_dispatch for backend abstraction

# ======================================================================================
# SINGLE-DEVICE EXAMPLES (work with all backends via can_dispatch)
# ======================================================================================
if(CONFIG_EXAMPLE_SEND_SINGLE OR CONFIG_EXAMPLE_RECV_POLL_SINGLE OR CONFIG_EXAMPLE_RECV_INT_SINGLE)
    # Select source file based on example type
    if(CONFIG_EXAMPLE_SEND_SINGLE)
        set(APP_SRC "${CMAKE_SOURCE_DIR}/components/twai-idf-can/examples/send/main/main.c")
    elseif(CONFIG_EXAMPLE_RECV_POLL_SINGLE)
        set(APP_SRC "${CMAKE_SOURCE_DIR}/components/twai-idf-can/examples/receive_poll/main/main.c")
    elseif(CONFIG_EXAMPLE_RECV_INT_SINGLE)
        set(APP_SRC "${CMAKE_SOURCE_DIR}/components/twai-idf-can/examples/receive_interrupt/main/main.c")
    endif()
    
    # Configure include paths based on selected backend
    set(EXTRA_INCLUDE_DIRS)
    
    if(CONFIG_CAN_BACKEND_TWAI)
        # TWAI backend: use original config_can.h from twai-idf-can/examples
        list(APPEND EXTRA_INCLUDE_DIRS
            "${CMAKE_SOURCE_DIR}/components/twai-idf-can/examples"
            "${CMAKE_SOURCE_DIR}/components/twai-idf-can/include"
        )
    elseif(CONFIG_CAN_BACKEND_MCP2515_SINGLE OR CONFIG_CAN_BACKEND_MCP2515_MULTI)
        # MCP backends: use wrapper config_can.h from examples/ (redirects to config_mcp25xxx_single.h)
        # Include path priority: examples/ comes first to override twai-idf-can/examples/config_can.h
        list(APPEND EXTRA_INCLUDE_DIRS
            "${CMAKE_SOURCE_DIR}/examples"
            "${CMAKE_SOURCE_DIR}/components/twai-idf-can/examples"
            "${CMAKE_SOURCE_DIR}/components/twai-idf-can/include"
        )
    endif()

# ======================================================================================
# MULTI-DEVICE EXAMPLES (use canif_* API from mcp25xxx-multi-idf-can directly)
# ======================================================================================
elseif(CONFIG_EXAMPLE_SEND_MULTI)
    set(APP_SRC "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/examples/send/main/main.c")
    set(EXTRA_INCLUDE_DIRS 
        "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/examples"
        "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/include"
    )
elseif(CONFIG_EXAMPLE_RECV_POLL_MULTI)
    set(APP_SRC "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/examples/receive_poll/main/main.c")
    set(EXTRA_INCLUDE_DIRS 
        "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/examples"
        "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/include"
    )
elseif(CONFIG_EXAMPLE_RECV_INT_MULTI)
    set(APP_SRC "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/examples/receive_interrupt/main/main.c")
    set(EXTRA_INCLUDE_DIRS 
        "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/examples"
        "${CMAKE_SOURCE_DIR}/components/mcp25xxx-multi-idf-can/include"
    )
endif()

# ======================================================================================
# Configure required components based on selected backend and example type
# ======================================================================================
# Note: examples-utils-idf-can is provided by example submodules via EXTRA_COMPONENT_DIRS

set(REQUIRES_DEPS)

# Single-device examples require can_dispatch for backend abstraction
if(CONFIG_EXAMPLE_SEND_SINGLE OR CONFIG_EXAMPLE_RECV_POLL_SINGLE OR CONFIG_EXAMPLE_RECV_INT_SINGLE)
    list(APPEND REQUIRES_DEPS can_dispatch examples-utils-idf-can)
    
    # Add backend-specific dependencies
    if(CONFIG_CAN_BACKEND_TWAI)
        list(APPEND REQUIRES_DEPS twai-idf-can)
    elseif(CONFIG_CAN_BACKEND_MCP2515_SINGLE)
        # mcp2515-esp32-idf is NOT a component (compiled directly in can_dispatch)
        # But we need mcp25xxx-multi-idf-can for type definitions
        list(APPEND REQUIRES_DEPS mcp25xxx-multi-idf-can)
    elseif(CONFIG_CAN_BACKEND_MCP2515_MULTI)
        list(APPEND REQUIRES_DEPS mcp25xxx-multi-idf-can)
    endif()

# Multi-device examples use mcp25xxx-multi-idf-can directly (no can_dispatch)
elseif(CONFIG_EXAMPLE_SEND_MULTI OR CONFIG_EXAMPLE_RECV_POLL_MULTI OR CONFIG_EXAMPLE_RECV_INT_MULTI)
    list(APPEND REQUIRES_DEPS mcp25xxx-multi-idf-can examples-utils-idf-can)
endif()

idf_component_register(
    SRCS ${APP_SRC}
    INCLUDE_DIRS "." ${EXTRA_INCLUDE_DIRS}
    REQUIRES ${REQUIRES_DEPS}
)
