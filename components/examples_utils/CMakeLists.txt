idf_component_register(
    SRCS "examples_utils.c"
    INCLUDE_DIRS "."
    REQUIRES  esp_timer can_backend_mcp2515_multi
)


