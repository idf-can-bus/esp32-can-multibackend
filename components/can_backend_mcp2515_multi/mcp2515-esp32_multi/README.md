# mcp2515-esp32_multi

High-level multi-device MCP2515 library for ESP-IDF with a stable public interface and a separate internal backend. Supports multiple MCP2515 controllers on one or more SPI busses, numeric bus/device IDs, and a thin facade API (`canif_*`) for messaging and control.

## Headers and layering

- Public API: `mcp2515_multi.h`
  - Configuration types: `mcp_spi_bus_config_t`, `mcp2515_device_config_t`, `mcp2515_bundle_config_t`
  - Numeric IDs/handles: `can_bus_id_t`, `can_dev_id_t`, `can_bus_handle_t`, `can_dev_handle_t`, `can_target_t`
  - Registry/lifecycle: `canif_register_bundle`, `canif_open_device`, `canif_open_all` ...
  - Messaging: `canif_send_to`, `canif_receive_from`, also `*_id`/`*_target`
  - Mode/bitrate, events, errors, filters/masks
  - Helper type: `can_message_t`

- Internal backend: `mcp2515_multi_internal.h`
  - Low-level SPI/MCP2515 control: `MCP2515_*` API
  - Not exported to users; subject to change

## Quick start

1) Provide bundle configuration (one SPI bus + N devices), ideally as a `const` in a header near your example/app:

```c
extern const mcp2515_bundle_config_t CAN_HW_CFG; // see examples for templates
```

2) Initialize and open all devices in the bundle:

```c
#include "mcp2515_multi.h"

canif_multi_init_default(&CAN_HW_CFG); // registers bundle and opens all devices
```

3) Send/receive per device:

```c
can_bus_handle_t bus = canif_bus_default();
for (size_t i = 0; i < canif_bus_device_count(bus); ++i) {
    can_dev_handle_t dev = canif_device_at(bus, i);
    can_message_t msg = { .id = 0x123, .dlc = 2, .data = { 0xDE, 0xAD } };
    (void)canif_send_to(dev, &msg);
}
```

## Naming conventions

- Public facade functions: `canif_*`
- Public configuration types: `mcp_*` (bus/device/bundle)
- Identifikátory a zprávy: `can_*` (`can_message_t`, `can_bus_id_t`, ...)
- Internal backend: `MCP2515_*`, `ERROR_t`

## Build (ESP-IDF component)

- Include directory exports only the public header; internal backend není určen pro přímé použití.
- Component depends on `driver`, `freertos`, `esp_timer`.

## Examples

Viz adresář `examples/` projektu: `examples/multi/*` používají výhradně `mcp2515_multi.h` a `canif_*` API.
