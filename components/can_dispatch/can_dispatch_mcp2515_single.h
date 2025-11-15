#pragma once
#include "driver/twai.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "mcp25xxx_multi.h"

#ifdef __cplusplus
extern "C" {
#endif


// Initialize MCP25xxx adapter
bool mcp2515_single_init(const mcp2515_bundle_config_t *cfg);

// Deinitialize MCP25xxx adapter
bool mcp2515_single_deinit();

// Send message
bool mcp2515_single_send(const twai_message_t *msg);

// Receive message
bool mcp2515_single_receive(twai_message_t *msg);

#ifdef __cplusplus
}
#endif