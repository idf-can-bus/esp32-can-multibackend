idf_component_register(
    SRCS "can_dispatch.c"
    INCLUDE_DIRS "."
    REQUIRES can_message can_backend_twai can_backend_mcp2515_single can_backend_mcp2515_multi
)
