set(SRCS "can_dispatch.c")
set(INCLUDE_DIRS ".")

# Local include dirs:
# - this component directory (public API)
# - twai-idf-can/include for can_twai_config.h and related types
set(INCLUDE_DIRS "."
    "${CMAKE_CURRENT_SOURCE_DIR}/../twai-idf-can/include"
)

# Always require mcp25xxx-multi-idf-can for shared types (mcp2515_bundle_config_t).
# TWAI implementation (twai-idf-can) is pulled in by the top-level application
# only when TWAI backend is selected, so we do not list it here to avoid
# linking TWAI code for MCP-only backends.
set(REQUIRES_DEPS mcp25xxx-multi-idf-can)

# Add MCP25xxx single adapter if enabled
if(CONFIG_CAN_BACKEND_MCP2515_SINGLE)
    list(APPEND SRCS "can_dispatch_mcp2515_single.c")
    # mcp2515-esp32-idf is NOT an ESP-IDF component, just a raw C library
    # We need to compile mcp2515.c directly and add its directory to includes
    list(APPEND SRCS "${CMAKE_CURRENT_SOURCE_DIR}/../mcp2515-esp32-idf/mcp2515.c")
    list(APPEND INCLUDE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/../mcp2515-esp32-idf")
endif()

idf_component_register(
    SRCS ${SRCS}
    INCLUDE_DIRS ${INCLUDE_DIRS}
    REQUIRES driver ${REQUIRES_DEPS}
)
