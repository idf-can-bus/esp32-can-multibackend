set(REQUIRES_DEPS)
list(APPEND REQUIRES_DEPS can_backend_mcp2515_multi)
if(CONFIG_CAN_BACKEND_TWAI)
    list(APPEND REQUIRES_DEPS twai-idf-can)
endif()
if(CONFIG_CAN_BACKEND_MCP2515_SINGLE)
    list(APPEND REQUIRES_DEPS can_backend_mcp2515_single)
endif()

idf_component_register(
    SRCS "can_dispatch.c"
    INCLUDE_DIRS "."
    REQUIRES ${REQUIRES_DEPS}
)
