idf_component_register(
    SRCS "twai_adapter.c" 
    INCLUDE_DIRS "."
    REQUIRES  driver can_backend_mcp2515_multi
)

# compile only if TWAI is selected in menuconfig
# if(NOT CONFIG_CAN_BACKEND_TWAI)
#     set_property(TARGET ${COMPONENT_LIB} PROPERTY EXCLUDE_FROM_ALL 1)
# endif()
