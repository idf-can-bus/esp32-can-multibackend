set(MULTI_SRC
  mcp2515_multi_adapter.c
  esp32-can-mcp2515-multi/src/mcp2515_multi.c
  esp32-can-mcp2515-multi/src/mcp2515_multi_internal.c
)

idf_component_register(
  SRCS ${MULTI_SRC}
  INCLUDE_DIRS "." "esp32-can-mcp2515-multi/include" "esp32-can-mcp2515-multi/src"
  REQUIRES driver freertos esp_timer
)

if(NOT CONFIG_CAN_BACKEND_MCP2515_MULTI)
  set_property(TARGET ${COMPONENT_LIB} PROPERTY EXCLUDE_FROM_ALL 1)
endif()
