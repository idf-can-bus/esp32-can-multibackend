#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "sdkconfig.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "can_message.h"


#ifdef __cplusplus
extern "C" {
#endif

// ======================================================================================
// Basic identifiers (must be defined before configuration types)
// ======================================================================================

// User-assigned compact identifiers (avoid strings to save RAM/flash)
typedef uint8_t can_bus_id_t;   // 0..255
typedef uint8_t can_dev_id_t;   // 0..255

// ======================================================================================
// Configuration types
// ======================================================================================

// ---------- SPI BUS (wiring + params) ----------
typedef struct {
    gpio_num_t miso_io_num;
    gpio_num_t mosi_io_num;
    gpio_num_t sclk_io_num;
    int        quadwp_io_num;  // -1 if unused
    int        quadhd_io_num;  // -1 if unused
} mcp_spi_bus_wiring_t;

typedef struct {
    spi_host_device_t host;      // SPIx_HOST
    int               max_transfer_sz; // 0 = default
    uint32_t          flags;     // SPICOMMON_BUSFLAG_*
    int               dma_chan;  // SPI_DMA_CH_AUTO or specific
    int               intr_flags;   // optional
    int               isr_cpu_id;   // optional
} mcp_spi_bus_params_t;

typedef struct {
    can_bus_id_t         bus_id;  // user-assigned ID (0..255)
    mcp_spi_bus_wiring_t wiring;
    mcp_spi_bus_params_t params;
    bool                 manage_bus_lifetime;
} mcp_spi_bus_config_t;

/*
 * Converts high-level SPI bus configuration to ESP-IDF spi_bus_config_t.
 * Parameters:
 *  - src:       pointer to high-level bus configuration (must be non-NULL)
 *  - out_host:  out parameter for SPI host identifier (SPIx_HOST)
 *  - out_bus_cfg: out parameter for IDF bus configuration
 *  - out_dma_chan: out parameter for DMA channel selection
 * Returns:
 *  - true if all pointers are valid and fields were filled; false otherwise.
 */
static inline bool mcp_spi_bus_to_idf(const mcp_spi_bus_config_t *src,
                                      spi_host_device_t *out_host,
                                      spi_bus_config_t *out_bus_cfg,
                                      int *out_dma_chan)
{
    if (!src || !out_host || !out_bus_cfg || !out_dma_chan) return false;
    *out_host = src->params.host;
    *out_dma_chan = src->params.dma_chan;
    out_bus_cfg->miso_io_num = src->wiring.miso_io_num;
    out_bus_cfg->mosi_io_num = src->wiring.mosi_io_num;
    out_bus_cfg->sclk_io_num = src->wiring.sclk_io_num;
    out_bus_cfg->quadwp_io_num = src->wiring.quadwp_io_num;
    out_bus_cfg->quadhd_io_num = src->wiring.quadhd_io_num;
    out_bus_cfg->max_transfer_sz = src->params.max_transfer_sz;
    out_bus_cfg->flags = src->params.flags;
    out_bus_cfg->intr_flags = src->params.intr_flags; // ensure valid interrupt flags
    return true;
}

// ---------- SPI DEVICE (wiring + params) ----------
typedef struct {
    gpio_num_t cs_gpio;
    gpio_num_t int_gpio;   // GPIO_NUM_NC if unused
    gpio_num_t stby_gpio;  // optional, GPIO_NUM_NC if unused
    gpio_num_t rst_gpio;   // optional, GPIO_NUM_NC if unused
} mcp_spi_dev_wiring_t;

typedef struct {
    uint8_t   mode;             // 0..3
    uint32_t  clock_speed_hz;   // e.g., 10 MHz
    uint32_t  queue_size;       // e.g., 64/1024
    uint32_t  flags;
    uint32_t  command_bits;
    uint32_t  address_bits;
    uint32_t  dummy_bits;
} mcp_spi_dev_params_t;

static inline void mcp_spi_dev_to_idf(const mcp_spi_dev_wiring_t *w,
                                      const mcp_spi_dev_params_t *p,
                                      spi_device_interface_config_t *out)
{
    /*
     * Fills ESP-IDF spi_device_interface_config_t from high-level device wiring/params.
     * Parameters:
     *  - w:   device wiring (CS pin must be valid)
     *  - p:   SPI device parameters (mode, clock, queue size, etc.)
     *  - out: target IDF config structure to populate
     */
    out->mode = p->mode;
    out->clock_speed_hz = p->clock_speed_hz;
    out->spics_io_num = w->cs_gpio;
    out->queue_size = p->queue_size;
    out->flags = p->flags;
    out->command_bits = p->command_bits;
    out->address_bits = p->address_bits;
    out->dummy_bits = p->dummy_bits;
}

// ---------- MCP2515 device (HW + CAN params) ----------

typedef enum {
    MCP_20MHZ,
    MCP_16MHZ,
    MCP_8MHZ
} CAN_CLOCK_t;


typedef enum {
    CAN_5KBPS,
    CAN_10KBPS,
    CAN_20KBPS,
    CAN_31K25BPS,
    CAN_33KBPS,
    CAN_40KBPS,
    CAN_50KBPS,
    CAN_80KBPS,
    CAN_83K3BPS,
    CAN_95KBPS,
    CAN_100KBPS,
    CAN_125KBPS,
    CAN_200KBPS,
    CAN_250KBPS,
    CAN_500KBPS,
    CAN_1000KBPS
} CAN_SPEED_t;

typedef struct {
    CAN_CLOCK_t crystal_frequency;   // MCP_8MHZ / MCP_16MHZ / MCP_20MHZ
} mcp2515_hw_t;

typedef struct {
    CAN_SPEED_t can_speed;      // CAN_500KBPS, CAN_1000KBPS, ...
    bool        use_loopback;   // optional test mode
} mcp2515_can_params_t;

typedef struct {
    // Device identification is provided separately (see Identification types section)
    uint8_t                dev_id;     // user-assigned device ID (0..255)
    mcp_spi_dev_wiring_t   wiring;     // device wiring
    mcp_spi_dev_params_t   spi_params; // SPI params
    mcp2515_hw_t           hw;         // MCP2515 HW params
    mcp2515_can_params_t   can;        // CAN params
} mcp2515_device_config_t;

// Bundle: one SPI bus with multiple MCP2515 devices
typedef struct {
    mcp_spi_bus_config_t       bus;    // contains user-assigned bus_id (0..255)
    const mcp2515_device_config_t *devices;
    size_t                     device_count;
} mcp2515_bundle_config_t;


// ======================================================================================
// Identification types
// ======================================================================================

// Opaque runtime handles (internals hidden from application)
typedef struct can_bus_handle_s* can_bus_handle_t;
typedef struct can_dev_handle_s* can_dev_handle_t;

// Composite target: top 8 bits = bus_id, low 8 bits = dev_id
typedef uint16_t can_target_t;
/*
 * Packs bus_id and dev_id into a compact target value.
 * The upper 8 bits hold bus_id; the lower 8 bits hold dev_id.
 */
static inline can_target_t can_target_from_ids(can_bus_id_t bus_id, can_dev_id_t dev_id) {
    return (can_target_t)(((uint16_t)bus_id << 8) | (uint16_t)dev_id);
}
/* Extracts bus_id (upper 8 bits) from a composite target. */
static inline can_bus_id_t can_target_bus_id(can_target_t t) { return (can_bus_id_t)(t >> 8); }
/* Extracts dev_id (lower 8 bits) from a composite target. */
static inline can_dev_id_t can_target_dev_id(can_target_t t) { return (can_dev_id_t)(t & 0xFF); }

// ======================================================================================
// Registry and lookup API
// ======================================================================================

// Returns number of registered SPI busses.
size_t            canif_bus_count(void);

// Returns handle of bus at index in range [0, canif_bus_count()).
can_bus_handle_t  canif_bus_at(size_t index);

// Returns number of devices registered on a bus handle.
size_t            canif_bus_device_count(can_bus_handle_t bus);

// Returns handle of device at index on given bus.
can_dev_handle_t  canif_device_at(can_bus_handle_t bus, size_t index);

// Returns bus handle by user-assigned ID (or NULL if not found).
can_bus_handle_t  canif_bus_get_by_id(can_bus_id_t bus_id);

// Returns device handle by bus/device IDs (or NULL if not found).
can_dev_handle_t  canif_dev_get_by_id(can_bus_id_t bus_id, can_dev_id_t dev_id);

// Validates that a bus/device handle is non-NULL and currently registered.
bool              canif_is_valid_bus(can_bus_handle_t bus);
bool              canif_is_valid_device(can_dev_handle_t dev);

// Returns default bus/device handles (application-defined; typically first configured).
can_bus_handle_t  canif_bus_default(void);
can_dev_handle_t  canif_device_default(void);

// Clears the internal registry of registered bundles. Use before re-registering.
void              canif_clear_registry(void);

// Registers a bundle (one SPI bus plus its devices) into the registry. Returns false if full.
bool              canif_register_bundle(const mcp2515_bundle_config_t* bundle);

// ======================================================================================
// Messaging operations
// ======================================================================================

// Sends a frame to the specified device handle.
// Returns true on successful queueing/transmission request.
bool              canif_send_to(can_dev_handle_t dev, const can_message_t* msg);

// Receives a frame from the specified device handle if available (non-blocking).
// Returns true if a frame was read into 'msg'.
bool              canif_receive_from(can_dev_handle_t dev, can_message_t* msg);

// Sends a frame using numeric IDs; resolves to the target device at runtime.
bool              canif_send_id(can_bus_id_t bus_id, can_dev_id_t dev_id, const can_message_t* msg);

// Receives a frame using numeric IDs; non-blocking.
bool              canif_receive_id(can_bus_id_t bus_id, can_dev_id_t dev_id, can_message_t* msg);

// Sends a frame using a composite target (bus_id | dev_id).
bool              canif_send_target(can_target_t target, const can_message_t* msg);

// Receives a frame using a composite target (non-blocking).
bool              canif_receive_target(can_target_t target, can_message_t* msg);

// High-level helpers for default device
bool              canif_multi_init_default(const mcp2515_bundle_config_t* cfg);
bool              canif_multi_deinit_default(void);
bool              canif_multi_send_default(const can_message_t* msg);
bool              canif_receive_default(can_message_t* msg);


// ======================================================================================
// Initialization & lifecycle
// ======================================================================================

// Opens a device: binds SPI device and initializes MCP2515 (reset, bitrate, mode).
// Returns true on success.
bool              canif_open_device(can_dev_handle_t dev);

// Closes a device: releases SPI device and related resources. Returns true on success.
bool              canif_close_device(can_dev_handle_t dev);

// Convenience wrappers using numeric IDs
bool              canif_open_id(can_bus_id_t bus_id, can_dev_id_t dev_id);
bool              canif_close_id(can_bus_id_t bus_id, can_dev_id_t dev_id);

// Convenience wrappers using composite target
bool              canif_open_target(can_target_t target);
bool              canif_close_target(can_target_t target);

// ======================================================================================
// Mode & bitrate control
// ======================================================================================

// Sets bitrate (CAN speed + oscillator) for a device handle. Returns true on success.
bool              canif_set_bitrate_to(can_dev_handle_t dev, CAN_SPEED_t speed, CAN_CLOCK_t clock);

// Switches device mode.
bool              canif_set_mode_normal(can_dev_handle_t dev);
bool              canif_set_mode_loopback(can_dev_handle_t dev);

// ID-based convenience variants
bool              canif_set_bitrate_id(can_bus_id_t bus_id, can_dev_id_t dev_id, CAN_SPEED_t s, CAN_CLOCK_t c);
bool              canif_set_mode_normal_id(can_bus_id_t bus_id, can_dev_id_t dev_id);
bool              canif_set_mode_loopback_id(can_bus_id_t bus_id, can_dev_id_t dev_id);

// Target-based convenience variants
bool              canif_set_bitrate_target(can_target_t t, CAN_SPEED_t s, CAN_CLOCK_t c);
bool              canif_set_mode_normal_target(can_target_t t);
bool              canif_set_mode_loopback_target(can_target_t t);

// ======================================================================================
// Events
// ======================================================================================

// Event callback type. The eventMask bits are backend-defined; 0 means no events.
typedef void (*canif_event_cb)(can_dev_handle_t dev, uint32_t eventMask, void* userData);

// Registers or updates an event callback for the device.
void              canif_set_event_callback(can_dev_handle_t dev, canif_event_cb cb, void* userData);

// Waits for device events with a timeout in ticks; returns OR-mask of events (or 0 on timeout).
uint32_t          canif_wait_for_event(can_dev_handle_t dev, uint32_t timeout_ticks);

// ======================================================================================
// Errors & diagnostics
// ======================================================================================

// Reads MCP2515 error flags (EFLG). 0 means no error.
uint8_t           canif_get_error_flags(can_dev_handle_t dev);

// Clears RX overrun related flags.
void              canif_clear_rx_overrun(can_dev_handle_t dev);

// Clears generic error interrupt flag.
void              canif_clear_error_int(can_dev_handle_t dev);

// ======================================================================================
// Filters & masks
// ======================================================================================

// Configures one acceptance filter (filter_idx 0..5). If 'extended' is true, 'id' is 29-bit.
bool              canif_set_filter(can_dev_handle_t dev, uint8_t filter_idx, bool extended, uint32_t id);

// Configures one acceptance mask (mask_idx 0..1). If 'extended' is true, 'mask' is 29-bit.
bool              canif_set_mask(can_dev_handle_t dev, uint8_t mask_idx, bool extended, uint32_t mask);

// ======================================================================================
// Introspection & utilities
// ======================================================================================

// Returns read-only device configuration for the given handle (or NULL if invalid).
const mcp2515_device_config_t*
                   canif_device_config(can_dev_handle_t dev);

// Extracts user-assigned IDs from handles.
can_bus_id_t       canif_bus_id_of(can_bus_handle_t bus);
can_dev_id_t       canif_dev_id_of(can_dev_handle_t dev);

// --------------------------------------------------------------------------------------
// Example: two SPI busses, two devices per bus (configuration + usage sketch)
// --------------------------------------------------------------------------------------
/*
// IDs for readability
#define BUS_MAIN   ((can_bus_id_t)1)
#define BUS_AUX    ((can_bus_id_t)2)
#define DEV_ENGINE ((can_dev_id_t)10)
#define DEV_DASH   ((can_dev_id_t)11)

static const mcp2515_device_config_t BUS_MAIN_DEVICES[] = {
    {
        .dev_id = DEV_ENGINE,
        .wiring = { .cs_gpio = GPIO_NUM_10, .int_gpio = GPIO_NUM_9, .stby_gpio = GPIO_NUM_NC, .rst_gpio = GPIO_NUM_NC },
        .spi_params = { .mode = 0, .clock_speed_hz = 10*1000*1000, .queue_size = 64 },
        .hw = { .crystal_frequency = MCP_16MHZ },
        .can = { .can_speed = CAN_500KBPS, .use_loopback = false },
    },
    {
        .dev_id = DEV_DASH,
        .wiring = { .cs_gpio = GPIO_NUM_11, .int_gpio = GPIO_NUM_8, .stby_gpio = GPIO_NUM_NC, .rst_gpio = GPIO_NUM_NC },
        .spi_params = { .mode = 0, .clock_speed_hz = 10*1000*1000, .queue_size = 64 },
        .hw = { .crystal_frequency = MCP_16MHZ },
        .can = { .can_speed = CAN_500KBPS, .use_loopback = false },
    },
};

static const mcp2515_bundle_config_t MAIN_BUNDLE = {
    .bus = {
        .bus_id = BUS_MAIN,
        .wiring = { .miso_io_num = GPIO_NUM_37, .mosi_io_num = GPIO_NUM_38, .sclk_io_num = GPIO_NUM_36, .quadwp_io_num = -1, .quadhd_io_num = -1 },
        .params = { .host = SPI2_HOST, .max_transfer_sz = 0, .flags = SPICOMMON_BUSFLAG_MASTER, .dma_chan = SPI_DMA_CH_AUTO },
        .manage_bus_lifetime = true,
    },
    .devices = BUS_MAIN_DEVICES,
    .device_count = 2,
};

// Initialize registry from bundles (high-level, conceptual)
// canif_register_bundle(&MAIN_BUNDLE);

// Operate by IDs
mcp_can_frame_t f = { .can_id = 0x123, .can_dlc = 2, .data = { 0xDE, 0xAD } };
canif_send_id(BUS_MAIN, DEV_ENGINE, &f);

// Operate by composite target
can_target_t tgt = can_target_from_ids(BUS_MAIN, DEV_DASH);
if (canif_receive_target(tgt, &f)) {
    // process
}

// Iterate all devices
for (size_t bi = 0; bi < canif_bus_count(); ++bi) {
    can_bus_handle_t b = canif_bus_at(bi);
    for (size_t di = 0; di < canif_bus_device_count(b); ++di) {
        can_dev_handle_t d = canif_device_at(b, di);
        (void)canif_send_to(d, &f);
    }
}
*/

#ifdef __cplusplus
}
#endif


