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
    // MCP25xxx single expects mcp2515_bundle_config_t
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
    // Multi backend expects mcp2515_bundle_config_t
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
