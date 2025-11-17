/**
 * @file can_dispatch.c
 * @brief CAN backend dispatcher implementation
 *
 * Provides unified can_twai_* API implementation for non-TWAI backends.
 * Maps TWAI-style calls to backend-specific functions.
 *
 * @author Ivo Marvan
 * @date 2025
 */

#include "can_dispatch.h"
#include "sdkconfig.h"

#if CONFIG_CAN_BACKEND_MCP2515_MULTI
#include "mcp25xxx_multi.h"
#endif

// ======================================================================================
// Backend identification overrides for dispatched single-device backends
// ======================================================================================

#if CONFIG_CAN_BACKEND_MCP2515_SINGLE
const char *can_backend_get_name(void)
{
    // For MCP2515 single backend, override the default multi-backend name
    // to clearly identify the 3rd-party single-controller driver.
    return "MCP2515 single";
}
#endif

// ======================================================================================
// Unified TWAI-style API implementation for non-TWAI backends
// ======================================================================================

#if CONFIG_CAN_BACKEND_MCP2515_SINGLE

// read header for adapter implementation
#include "can_dispatch_mcp2515_single.h"

// --------------------------------------------------------------------------------------
// MCP25xxx Single backend: map can_twai_* → mcp2515_single_*
// --------------------------------------------------------------------------------------

bool can_twai_init(const twai_backend_config_t *cfg)
{
    // NOTE:
    //  - For TWAI examples, cfg is obtained from TWAI_HW_CFG.
    //  - In the multi-backend project, TWAI_HW_CFG is an alias that actually
    //    refers to MCP_SINGLE_HW_CFG (type mcp2515_bundle_config_t) defined
    //    in examples/can_single_MCP25xxx_config.h.
    //  - We therefore safely reinterpret the pointer here and pass it to the
    //    MCP2515 single adapter.
    return mcp2515_single_init((const mcp2515_bundle_config_t *)cfg);
}

bool can_twai_deinit(void)
{
    return mcp2515_single_deinit();
}

bool can_twai_send(const twai_message_t *msg)
{
    return mcp2515_single_send(msg);
}

bool can_twai_receive(twai_message_t *msg)
{
    return mcp2515_single_receive(msg);
}

void can_twai_reset_if_needed(void)
{
    // MCP25xxx handles reset differently - no-op here
}

#elif CONFIG_CAN_BACKEND_MCP2515_MULTI
// --------------------------------------------------------------------------------------
// MCP25xxx Multi backend: map can_twai_* → canif_multi_*
// --------------------------------------------------------------------------------------

bool can_twai_init(const twai_backend_config_t *cfg)
{
    // Multi backend expects mcp2515_bundle_config_t; in the single-example
    // path, cfg is a twai_backend_config_t-compatible alias pointing to a
    // mcp2515_bundle_config_t instance (see examples/config_twai.h).
    return canif_multi_init_default((const mcp2515_bundle_config_t *)cfg);
}

bool can_twai_deinit(void)
{
    return canif_multi_deinit_default();
}

bool can_twai_send(const twai_message_t *msg)
{
    return canif_multi_send_default(msg);
}

bool can_twai_receive(twai_message_t *msg)
{
    return canif_receive_default(msg);
}

void can_twai_reset_if_needed(void)
{
    // MCP25xxx handles reset differently - no-op here
}

#elif CONFIG_CAN_BACKEND_TWAI
// --------------------------------------------------------------------------------------
// TWAI backend: Native implementation from twai-idf-can component
// --------------------------------------------------------------------------------------
// No implementation needed here - functions are provided by twai-idf-can component
// This block is here for documentation and completeness

#else
#error "Unknown CAN backend configuration"
#endif
