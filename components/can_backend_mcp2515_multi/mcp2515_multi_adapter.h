#pragma once
#include "driver/twai.h"
#include "mcp2515_multi_internal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef MCP2515_Handle mcp_multi_handle_t;

typedef struct {
    // One instance configuration
    spi_host_device_t host;
    spi_bus_config_t  bus_cfg;
    spi_device_interface_config_t dev_cfg;
    gpio_num_t        int_gpio;
    CAN_SPEED_t       can_speed;
    CAN_CLOCK_t       can_clock;
} mcp_multi_instance_cfg_t;

bool mcp2515_multi_init(const mcp_multi_instance_cfg_t* instances, size_t count);
bool mcp2515_multi_deinit(void);

// Index-based send/receive to a specific instance
bool mcp2515_multi_send(size_t index, const twai_message_t* msg);
bool mcp2515_multi_receive(size_t index, twai_message_t* msg);

#ifdef __cplusplus
}
#endif


