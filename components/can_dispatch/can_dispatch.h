/**
 * @file can_dispatch.h
 * @brief CAN backend dispatcher - unified TWAI-style API for all backends
 * 
 * This dispatcher provides a unified can_twai_* API that works with multiple
 * CAN backends (TWAI, MCP25xxx single, MCP25xxx multi). Examples written for
 * TWAI can work with any backend through this abstraction layer.
 * 
 * Architecture:
 * - Single examples use can_twai_* API (this file provides declarations)
 * - Multi examples use canif_* API from mcp25xxx_multi.h directly
 * - Backend selection via Kconfig (CONFIG_CAN_BACKEND_*)
 * - Examples include their own headers (can_twai.h, config_twai.h, etc.)
 * 
 * For TWAI backend: Examples include can_twai.h directly (native implementation)
 * For other backends: This file provides can_twai_* wrapper declarations
 * 
 * @author Ivo Marvan
 * @date 2025
 */

#pragma once
#include <stdint.h>
#include <stdbool.h>
#include "driver/twai.h"
#include "sdkconfig.h"

// Include can_twai_config.h for type definition
// (needed for function declarations even in non-TWAI backends)
#include "can_twai_config.h"

#ifdef __cplusplus
extern "C" {
#endif

// ======================================================================================
// Unified TWAI-style API for single device examples
// ======================================================================================
/**
 * @brief Unified CAN API using TWAI naming convention
 * 
 * These functions provide a consistent interface across all backends:
 * - For TWAI backend: Uses native TWAI functions (from twai-idf-can component)
 * - For MCP25xxx backends: can_dispatch maps to appropriate MCP25xxx functions
 * 
 * This allows single-device examples to work with any backend without modification.
 */

#if !CONFIG_CAN_BACKEND_TWAI
// Only provide implementations for non-TWAI backends
// (TWAI backend uses native functions from twai-idf-can component)

/**
 * @brief Initialize CAN hardware
 * @param cfg Backend-specific configuration
 * @return true on success, false otherwise
 */
bool can_twai_init(const twai_backend_config_t *cfg);

/**
 * @brief Deinitialize CAN hardware
 * @return true on success, false otherwise
 */
bool can_twai_deinit(void);

/**
 * @brief Send CAN message (non-blocking)
 * @param msg Pointer to TWAI message structure
 * @return true on success, false otherwise
 */
bool can_twai_send(const twai_message_t *msg);

/**
 * @brief Receive CAN message (non-blocking)
 * @param msg Pointer to TWAI message structure to fill
 * @return true if message received, false if no message available
 */
bool can_twai_receive(twai_message_t *msg);

/**
 * @brief Reset TWAI controller if needed
 * 
 * For TWAI backend, performs actual reset.
 * For MCP25xxx backends, no-op (reset handled differently).
 */
void can_twai_reset_if_needed(void);

#endif // !CONFIG_CAN_BACKEND_TWAI

#ifdef __cplusplus
}
#endif
