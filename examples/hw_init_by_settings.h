#pragma once

#include "can_dispatch.h"
#include "sdkconfig.h"

// Include the example's header-only HW configuration based on selected backend.
#if CONFIG_CAN_BACKEND_TWAI
#include "single/config_hw_twai.h"
#elif CONFIG_CAN_BACKEND_MCP2515_SINGLE
#include "single/config_hw_mcp2515_single.h"
#elif CONFIG_CAN_BACKEND_MCP2515_MULTI
#include "config_hw_mcp2515_multiple.h"
#endif
