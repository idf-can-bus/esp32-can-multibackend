set(SRCS "can_dispatch.c")
set(REQUIRES_DEPS)

# Add TWAI adapter if enabled
if(CONFIG_CAN_BACKEND_TWAI)
    list(APPEND REQUIRES_DEPS twai-idf-can)
endif()

# Add MCP2515 single adapter if enabled
if(CONFIG_CAN_BACKEND_MCP2515_SINGLE)
    list(APPEND SRCS "can_dispatch_mcp2515_single.c")
    list(APPEND REQUIRES_DEPS mcp2515-esp32-idf)
endif()

# Add MCP2515 multi adapter if enabled  
if(CONFIG_CAN_BACKEND_MCP2515_MULTI)
    list(APPEND REQUIRES_DEPS mcp25xxx-multi-idf-can)
endif()

idf_component_register(
    SRCS ${SRCS}
    INCLUDE_DIRS "."
    REQUIRES driver ${REQUIRES_DEPS}
)
