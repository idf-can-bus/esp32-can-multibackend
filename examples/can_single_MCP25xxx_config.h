/**
 * @file can_single_MCP25xxx_config.h
 * @brief Hardware configuration for single MCP25xxx device examples
 * 
 * This configuration is used for all single-device MCP25xxx examples
 * (send, receive_poll, receive_interrupt) with both MCP2515 Single
 * and MCP25xxx Multi backends.
 * 
 * Hardware setup.
 * 
 * **IMPORTANT:** Adapt GPIO pins, SPI host, crystal frequency, and CAN bitrate
 * to match your actual hardware before building the examples.
 * 
 * @note GPIO pin assignments are for ESP32-S3. Other ESP32 variants may
 *       require different pin selections.
 * 
 * @author Ivo Marvan
 * @date 2025
 */

 #pragma once

 #include "driver/gpio.h"
 #include "driver/spi_master.h"
 #include "mcp25xxx_multi.h"
 
 /**
  * @brief Single MCP25xxx device configuration
  * 
  * This configuration is used by can_dispatch layer to initialize
  * either mcp2515-esp32-idf (single) or mcp25xxx-multi-idf-can (with 1 device).
  * 
  * The configuration is cast to twai_backend_config_t* in can_dispatch.h
  * for compatibility with unified API.
  */
 const mcp2515_bundle_config_t MCP_SINGLE_HW_CFG = {
     // SPI Bus Configuration
     .bus = {
         .bus_id = (can_bus_id_t)1,
         .wiring = {
             .miso_io_num   = GPIO_NUM_37,  // SPI MISO pin
             .mosi_io_num   = GPIO_NUM_38,  // SPI MOSI pin
             .sclk_io_num   = GPIO_NUM_36,  // SPI SCLK pin
             .quadwp_io_num = -1,           // Unused (quad SPI mode)
             .quadhd_io_num = -1,           // Unused (quad SPI mode)
         },
         .params = {
             .host            = SPI2_HOST,            // SPI2 host
             .max_transfer_sz = 0,                    // Default (4096 bytes)
             .flags           = SPICOMMON_BUSFLAG_MASTER,
             .dma_chan        = SPI_DMA_CH_AUTO,      // Auto-select DMA channel
             .intr_flags      = 0,                    // Default interrupt flags
             .isr_cpu_id      = 0,                    // Run ISR on CPU 0
         },
         .manage_bus_lifetime = true,  // Library manages SPI bus init/deinit
     },
     
     // Single MCP25xxx Device Configuration
     .devices = (const mcp2515_device_config_t[]){
         {
             .dev_id = (can_dev_id_t)1,
             .wiring = {
                 .cs_gpio   = GPIO_NUM_33,      // Chip Select pin
                 .int_gpio  = GPIO_NUM_34,      // Interrupt pin (required for receive_interrupt)
                 .stby_gpio = (gpio_num_t)-1,   // Standby pin (unused)
                 .rst_gpio  = (gpio_num_t)-1,   // Hardware reset pin (unused)
             },
             .spi_params = {
                 .mode            = 0,          // SPI mode 0 (CPOL=0, CPHA=0)
                 .clock_speed_hz  = 10000000,   // 10 MHz SPI clock
                 .queue_size      = 64,         // Transaction queue depth
                 .flags           = 0,          // No special device flags
                 .command_bits    = 0,          // No command phase
                 .address_bits    = 0,          // No address phase
                 .dummy_bits      = 0,          // No dummy bits
             },
             .hw = {
                 .crystal_frequency = MCP25XXX_16MHZ,  // 16 MHz crystal oscillator
             },
             .can = {
                 .can_speed     = MCP25XXX_1000KBPS,   // 1 Mbps CAN bitrate
                 .use_loopback  = false,               // Normal mode (not loopback)
             },
         },
     },
     .device_count = 1,  // Single device
 };
 
 