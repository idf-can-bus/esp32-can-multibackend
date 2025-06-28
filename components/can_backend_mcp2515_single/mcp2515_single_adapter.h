#pragma once
#include "can_iface.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

// MCP2515_SINGLE configuration
typedef struct {
    spi_bus_config_t spi_bus;      // SPI bus configuration
    spi_device_interface_config_t spi_dev;  // SPI device configuration
    gpio_num_t int_pin;            // Interrupt pin
    uint32_t baudrate;             // CAN bus baudrate
    spi_host_device_t spi_host;    // SPI host device
} mcp2515_single_config_t;

// Initialize MCP2515
bool mcp2515_single_init(const mcp2515_single_config_t *cfg);

// Deinitialize MCP2515
bool mcp2515_single_deinit();

// Send message
bool mcp2515_single_send(const can_message_t *raw_out_msg);

// Receive message
bool mcp2515_single_receive(can_message_t *raw_in_msg);

#ifdef __cplusplus
}
#endif