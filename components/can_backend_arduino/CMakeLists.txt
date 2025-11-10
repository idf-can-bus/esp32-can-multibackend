idf_component_register(
  SRCS "arduino_adapter.c"
  INCLUDE_DIRS "."
  REQUIRES can_dispatch can_backend_mcp2515_multi
)

if(NOT CONFIG_CAN_BACKEND_ARDUINO)
  set_property(TARGET ${COMPONENT_LIB} PROPERTY EXCLUDE_FROM_ALL 1)
endif()
