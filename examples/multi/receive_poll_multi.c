#include "can_dispatch.h"
#include "mcp2515_multi_if.h"
#include <stdio.h>
#include "examples_utils.h"
#include "../hw_init_by_settings.h"
#include "esp_log.h"

static const char *TAG = "receive_poll_multi";

void app_main(void)
{
    // Initialize hardware via header-only configuration and can_dispatch
    init_hw();

    const uint32_t receive_interval_ms = 1;
    can_message_t msg;

    can_bus_handle_t bus = canif_bus_default();
    size_t n = canif_bus_device_count(bus);

    ESP_LOGI(TAG, "Receiver poll-driven, MCP2515 multi, %zu instances", n);
    while (1) {
        // poll all instances
        for (size_t i=0; i<n; ++i) {
            can_dev_handle_t dev = canif_device_at(bus, i);
            if (canif_receive_from(dev, &msg)) {
                process_received_message_multi(&msg, false);
            }
        }
        sleep_ms_min_ticks(receive_interval_ms);
    }
}
