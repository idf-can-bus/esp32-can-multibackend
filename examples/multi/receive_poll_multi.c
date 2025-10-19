#include "can_dispatch.h"
#include <stdio.h>
#include "examples_utils.h"
#include "init_hardware.h"
#include "mcp2515_multi_adapter.h"
#include "esp_log.h"

static const char *TAG = "receive_poll_multi";

void app_main(void)
{
    // Hardware init creates three instances; we will poll them by index
    can_config_t dummy_cfg;
    init_hardware(&dummy_cfg);

    const uint32_t receive_interval_ms = 1;
    can_message_t msg;

    size_t n = can_configured_instance_count();

    ESP_LOGI(TAG, "Receiver poll-driven, MCP2515 multi, %zu instances", n);
    while (1) {
        // poll all instances
        for (size_t i=0; i<n; ++i) {
            if (mcp2515_multi_receive(i, &msg)) {
                process_received_message_multi(&msg, false);
            }
        }
        sleep_ms_min_ticks(receive_interval_ms);
    }
}
