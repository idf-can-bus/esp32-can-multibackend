#pragma once
#include "can_message.h"
#include "driver/twai.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "twai_config_types.h"

#ifdef __cplusplus
extern "C" {
#endif




// Initialize CAN hardware
bool can_twai_init(const twai_backend_config_t *cfg);

// Deinitialize CAN hardware
bool can_twai_deinit();

// non-blocking send
bool can_twai_send(const can_message_t *raw_out_msg);

// non-blocking receive
bool can_twai_receive(can_message_t *raw_in_msg);

/**
 * Checks TWAI controller status and resets it if necessary.
 * This handles bus-off conditions and restarts the controller
 * if it's not in the running state.
 */
void can_twai_reset_twai_if_needed(void);

#ifdef __cplusplus
}
#endif