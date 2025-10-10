#pragma once
#include "can_iface.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "mcp2515-esp32-idf/mcp2515.h"

#ifdef __cplusplus
extern "C" {
#endif


// MCP2515_SINGLE configuration
typedef struct {
    spi_bus_config_t spi_bus;      // SPI bus configuration
    spi_device_interface_config_t spi_dev;  // SPI device configuration
    gpio_num_t int_pin;                    // Interrupt pin
    CAN_SPEED_t can_speed;                 // CAN bus speed (from mcp2515.h)
    CAN_CLOCK_t can_clock;                 // MCP2515 crystal frequency (from mcp2515.h)
    spi_host_device_t spi_host;    // SPI host device
    bool use_loopback;              // Use loopback mode for testing
    bool enable_debug_spi;          // Enable SPI/link diagnostics at runtime
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