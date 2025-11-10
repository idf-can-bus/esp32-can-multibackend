# Only build this component when the MCP2515_SINGLE backend is enabled
if(NOT CONFIG_CAN_BACKEND_MCP2515_SINGLE)
    return()
endif()

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
  REQUIRES can_backend_mcp2515_multi
  PRIV_REQUIRES driver
)
