idf_component_register(
  SRCS "mcp2515_multi_adapter.c"
  INCLUDE_DIRS "."
  PRIV_REQUIRES can_iface driver
)

if(NOT CONFIG_CAN_BACKEND_MCP2515_MULTI)
  set_property(TARGET ${COMPONENT_LIB} PROPERTY EXCLUDE_FROM_ALL 1)
endif()
