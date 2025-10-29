#pragma once

#include "driver/twai.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

// Split TWAI configuration into wiring + params + timing/filter + timeouts.

// GPIO wiring for TWAI controller
typedef struct {
    gpio_num_t tx_gpio;     // TX pin
    gpio_num_t rx_gpio;     // RX pin
    gpio_num_t clkout_io;   // TWAI_IO_UNUSED if not used
    gpio_num_t bus_off_io;  // TWAI_IO_UNUSED if not used
} twai_wiring_config_t;

// Controller parameters (non-GPIO)
typedef struct {
    int              controller_id;  // e.g., 0
    twai_mode_t      mode;           // TWAI_MODE_NORMAL, LISTEN_ONLY, LOOPBACK, etc.
    int              tx_queue_len;   // e.g., 20
    int              rx_queue_len;   // e.g., 20
    uint32_t         alerts_enabled; // TWAI_ALERT_*
    int              clkout_divider; // 0 to disable
    int              intr_flags;     // ESP_INTR_FLAG_*
} twai_params_config_t;

// Bit timing and acceptance filter
typedef struct {
    twai_timing_config_t timing;     // e.g., TWAI_TIMING_CONFIG_1MBITS()
    twai_filter_config_t filter;     // e.g., TWAI_FILTER_CONFIG_ACCEPT_ALL()
} twai_tf_config_t;

// Runtime timeouts
typedef struct {
    TickType_t receive_timeout;         // in ticks
    TickType_t transmit_timeout;        // in ticks
    TickType_t bus_off_timeout;         // in ticks
    TickType_t bus_not_running_timeout; // in ticks
} twai_timeouts_config_t;

// Full TWAI configuration composed of parts
typedef struct {
    twai_wiring_config_t   wiring;
    twai_params_config_t   params;
    twai_tf_config_t       tf;
    twai_timeouts_config_t timeouts;
} twai_backend_config_t;

