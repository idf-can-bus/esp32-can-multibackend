#pragma once

// Custom SPI device configuration and MCP2515 device config split into wiring and parameters.

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "components/can_backend_mcp2515_single/mcp2515-esp32-idf/mcp2515.h"

#ifdef __cplusplus
extern "C" {
#endif

// SPI device wiring (board connections)
typedef struct {
    gpio_num_t cs_gpio;    // CS pin
    gpio_num_t int_gpio;   // INT pin (GPIO_NUM_NC if unused)
    gpio_num_t stby_gpio;  // optional STBY pin (GPIO_NUM_NC if unused)
    gpio_num_t rst_gpio;   // optional RESET pin (GPIO_NUM_NC if unused)
} spi_device_wiring_config_t_ex;

// SPI device parameters (IF level)
typedef struct {
    uint8_t   mode;             // SPI mode 0..3
    uint32_t  clock_speed_hz;   // e.g., 10 MHz
    uint32_t  queue_size;       // e.g., 64/1024
    uint32_t  flags;            // device flags
    uint32_t  command_bits;
    uint32_t  address_bits;
    uint32_t  dummy_bits;
} spi_device_params_config_t_ex;

// MCP2515 hardware parameters
typedef struct {
    CAN_CLOCK_t crystal_frequency;   // MCP_8MHZ / MCP_16MHZ / MCP_20MHZ
} mcp2515_hardware_config_t_ex;

// CAN parameters
typedef struct {
    CAN_SPEED_t can_speed;      // CAN_500KBPS, CAN_1000KBPS, ...
    bool        use_loopback;   // optional test mode
} mcp2515_params_config_t_ex;

// Full device configuration
typedef struct {
    spi_device_wiring_config_t_ex  wiring;
    spi_device_params_config_t_ex  spi_params;
    mcp2515_hardware_config_t_ex   hw;
    mcp2515_params_config_t_ex     can;
} mcp2515_device_config_ex_t;

// Bundle: one SPI bus with multiple MCP2515 devices (array + count)
typedef struct {
    // forward-declared in spi_bus_config.h
    struct spi_bus_config_ex_t_opaque_tag* _opaque; // not used; keep C compatibility if needed
} _opaque_guard;

typedef struct {
    // Include bus separately from spi_bus_config.h to avoid circular include here
    // Users should compose (spi_bus_config_ex_t bus, mcp2515_device_config_ex_t* devices, size)
    const void *bus_ptr;                      // pointer cast to spi_bus_config_ex_t
    const mcp2515_device_config_ex_t *devices;
    size_t device_count;
} mcp2515_bus_bundle_ex_t;

// Converter to esp-idf spi_device_interface_config_t (no side effects)
static inline void spi_device_config_ex_to_idf(const spi_device_wiring_config_t_ex *w,
                                               const spi_device_params_config_t_ex *p,
                                               spi_device_interface_config_t *out)
{
    out->mode = p->mode;
    out->clock_speed_hz = p->clock_speed_hz;
    out->spics_io_num = w->cs_gpio;
    out->queue_size = p->queue_size;
    out->flags = p->flags;
    out->command_bits = p->command_bits;
    out->address_bits = p->address_bits;
    out->dummy_bits = p->dummy_bits;
}

#ifdef __cplusplus
}
#endif


