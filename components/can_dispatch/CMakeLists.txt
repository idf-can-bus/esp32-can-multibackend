set(SRCS "can_dispatch.c")
set(INCLUDE_DIRS ".")

# Always require these for type definitions used in headers:
# - twai-idf-can: twai_backend_config_t, twai_message_t (for all single examples)
# - mcp25xxx-multi-idf-can: mcp2515_bundle_config_t (used in can_dispatch_mcp2515_single.h)
set(REQUIRES_DEPS twai-idf-can mcp25xxx-multi-idf-can)

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
