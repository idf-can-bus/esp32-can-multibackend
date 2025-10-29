#pragma once

// Custom SPI bus configuration for esp-idf projects where we want a clear split
// between wiring and parameters, without relying on esp-idf's spi_bus_config_t
// as the canonical structure. Conversion helpers are provided to generate
// spi_bus_config_t and related values when needed.

#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

// Pure wiring for SPI bus (GPIO assignment)
typedef struct {
    gpio_num_t miso_io_num;    // required
    gpio_num_t mosi_io_num;    // required
    gpio_num_t sclk_io_num;    // required
    int        quadwp_io_num;  // -1 if unused
    int        quadhd_io_num;  // -1 if unused
} spi_bus_wiring_config_t_ex;

// Non-GPIO parameters for SPI bus
typedef struct {
    spi_host_device_t host;      // SPIx_HOST
    int               max_transfer_sz; // 0 = esp-idf default
    uint32_t          flags;     // SPICOMMON_BUSFLAG_*
    int               dma_chan;  // SPI_DMA_CH_AUTO or explicit channel
    int               intr_flags;   // ESP_INTR_FLAG_* (optional)
    int               isr_cpu_id;   // INTR_CPU_ID_AUTO or CPU id (optional)
} spi_bus_params_config_t_ex;

// Full bus configuration in parts
typedef struct {
    spi_bus_wiring_config_t_ex wiring;   // GPIO pins
    spi_bus_params_config_t_ex params;   // host + parameters
    bool manage_bus_lifetime;            // init/free the bus in code using this config
} spi_bus_config_ex_t;

// Helper macro for array size
#ifndef COUNT_OF
#define COUNT_OF(arr) (sizeof(arr)/sizeof((arr)[0]))
#endif

// Conversion helper to esp-idf types (no side effects)
// Returns true on success; outputs:
//  - *out_host: spi_host_device_t to use with esp-idf
//  - *out_bus_cfg: populated spi_bus_config_t constructed from wiring/params
//  - *out_dma_chan: dma channel to pass to spi_bus_initialize
static inline bool spi_bus_config_ex_to_idf(const spi_bus_config_ex_t *src,
                                            spi_host_device_t *out_host,
                                            spi_bus_config_t *out_bus_cfg,
                                            int *out_dma_chan)
{
    if (!src || !out_host || !out_bus_cfg || !out_dma_chan) {
        return false;
    }
    *out_host = src->params.host;
    *out_dma_chan = src->params.dma_chan;
    // Map to esp-idf spi_bus_config_t
    out_bus_cfg->miso_io_num = src->wiring.miso_io_num;
    out_bus_cfg->mosi_io_num = src->wiring.mosi_io_num;
    out_bus_cfg->sclk_io_num = src->wiring.sclk_io_num;
    out_bus_cfg->quadwp_io_num = src->wiring.quadwp_io_num;
    out_bus_cfg->quadhd_io_num = src->wiring.quadhd_io_num;
    out_bus_cfg->max_transfer_sz = src->params.max_transfer_sz;
    out_bus_cfg->flags = src->params.flags;
    // Note: intr_flags and isr_cpu_id are not fields of spi_bus_config_t;
    // they can be applied when allocating interrupts if needed by higher layers.
    return true;
}

#ifdef __cplusplus
}
#endif


