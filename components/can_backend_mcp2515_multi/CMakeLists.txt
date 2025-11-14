set(MULTI_SRC
  mcp2515_multi_adapter.c
  mcp25xxx-multi-idf-can/src/mcp2515_multi.c
  mcp25xxx-multi-idf-can/src/mcp2515_multi_internal.c
)

idf_component_register(
  SRCS ${MULTI_SRC}
  INCLUDE_DIRS "." "mcp25xxx-multi-idf-can/include" "mcp25xxx-multi-idf-can/src"
  REQUIRES driver freertos esp_timer
)

if(NOT CONFIG_CAN_BACKEND_MCP2515_MULTI)
  set_property(TARGET ${COMPONENT_LIB} PROPERTY EXCLUDE_FROM_ALL 1)
endif()
