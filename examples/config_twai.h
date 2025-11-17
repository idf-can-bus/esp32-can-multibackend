/**
 * @file config_twai.h
 * @brief Backend-agnostic hardware configuration wrapper for single-device examples
 *
 * This header is used only in the multi-backend integration project
 * (can-multibackend-idf). It provides a unified TWAI-style configuration
 * symbol (TWAI_HW_CFG) that maps to the single MCP25xxx bundle configuration
 * defined in can_single_MCP25xxx_config.h.
 *
 * The example code (main.c) in twai-idf-can includes "config_twai.h" and
 * expects a twai_backend_config_t-compatible handle. In this project, we
 * reinterpret that handle to point to MCP_SINGLE_HW_CFG, which is later
 * cast back to mcp2515_bundle_config_t * inside the can_dispatch layer.
 *
 * The twai-idf-can submodule itself remains unchanged.
 */

#pragma once

#include "can_twai_config.h"
#include "can_single_MCP25xxx_config.h"

/**
 * @brief Unified configuration alias for single MCP25xxx backend
 *
 * TWAI_HW_CFG is expected by the TWAI examples. Here it is defined as a
 * reinterpreted view of MCP_SINGLE_HW_CFG so that:
 *   &TWAI_HW_CFG  → (const twai_backend_config_t *)&MCP_SINGLE_HW_CFG
 *
 * The can_dispatch implementation for MCP backends then casts this pointer
 * back to (const mcp2515_bundle_config_t *) when calling the underlying
 * MCP25xxx driver functions.
 */
#define TWAI_HW_CFG (*(const twai_backend_config_t *)&MCP_SINGLE_HW_CFG)


