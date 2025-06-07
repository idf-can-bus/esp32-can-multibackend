#include "can_dispatch.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>
#include "esp_log.h"
#include "can_dispatch.h"
#include "examples_utils.h"
#include "init_hardware.h"

static const char *TAG = "receive_poll_single";


void app_main(void)
{

    // --- init hardware ----------------------------------------------------------------------------
    can_config_t hw_config;
    init_hardware(&hw_config);

    // --- common sender example part ---------------------------------------------------------------
    canif_init(&hw_config);

    // --- global variables -------------------------------------------------------------------------
    can_message_t message;
    uint8_t expected_heartbeat = 0;
    latency_statistic_t latency_statistic;
    bool success = false;

    // --- example settings ------------------------------------------------------------------------
    bool print_during_send = false;
    const uint32_t receive_interval_ms = 1;

    reset_latency_statistic(&latency_statistic);

    while (1)
    {
        // send message
        success = canif_receive(&message);
        if (success)
        {
            process_received_message(&message, &latency_statistic, &expected_heartbeat, print_during_send);
        } else {
            // wait a while
            vTaskDelay(pdMS_TO_TICKS(receive_interval_ms));
        }
    }
}
