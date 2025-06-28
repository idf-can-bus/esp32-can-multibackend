# local adapter
set(local_srcs "mcp2515_single_adapter.c")
set(local_includes ".")

# submodule sources
set(submodule_srcs
    "mcp2515-esp32-idf/mcp2515.c"
)
set(submodule_includes
    "mcp2515-esp32-idf"
)

idf_component_register(
  SRCS ${local_srcs} ${submodule_srcs}
  INCLUDE_DIRS ${local_includes} ${submodule_includes}
  PRIV_REQUIRES can_iface driver
)

# Exclude if not selected in menuconfig
if(NOT CONFIG_CAN_BACKEND_MCP2515_SINGLE)
  set_property(TARGET ${COMPONENT_LIB} PROPERTY EXCLUDE_FROM_ALL 1)
endif()
