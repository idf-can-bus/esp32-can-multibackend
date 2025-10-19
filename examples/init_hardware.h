#pragma once

#include "can_dispatch.h"

void init_hardware(can_config_t *hw_config_ptr);

// Return number of configured CAN controller instances (for MULTI adapter).
// For TWAI and SINGLE backends returns 1.
size_t can_configured_instance_count(void);
