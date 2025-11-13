#include "driver/twai.h"
#include "mcp2515_multi_adapter.h"
#include "esp_log.h"

static const char* TAG = "mcp2515_multi_adapter";

static MCP2515_Handle *g_handles = NULL;
static size_t g_count = 0;

// Convert twai_message_t to CAN_FRAME
static inline void to_frame(const twai_message_t *in, CAN_FRAME *out)
{
    // Check if extended frame flag is set
    bool is_extended = (in->flags & TWAI_MSG_FLAG_EXTD) != 0;
    out->can_id = is_extended ? (in->identifier | (1u << 31)) : (in->identifier & 0x7FF);
    out->can_dlc = in->data_length_code;
    for (int i = 0; i < in->data_length_code; i++) {
        out->data[i] = in->data[i];
    }
}

// Convert CAN_FRAME to twai_message_t
static inline void from_frame(const CAN_FRAME *in, twai_message_t *out)
{
    bool ext = (in->can_id & (1u << 31)) != 0;
    out->flags = ext ? TWAI_MSG_FLAG_EXTD : 0;
    out->identifier = ext ? (in->can_id & 0x1FFFFFFF) : (in->can_id & 0x7FF);
    out->data_length_code = in->can_dlc;
    for (int i = 0; i < in->can_dlc; i++) {
        out->data[i] = in->data[i];
    }
}

bool mcp2515_multi_init(const mcp_multi_instance_cfg_t* instances, size_t count)
{
    if (!instances || count == 0) return false;
    if (g_handles) return false; // already initialized

    g_handles = (MCP2515_Handle*)calloc(count, sizeof(MCP2515_Handle));
    if (!g_handles) return false;

    for (size_t i=0; i<count; ++i) {
        mcp2515_multi_config_t cfg = {
            .can_speed = instances[i].can_speed,
            .can_clock = instances[i].can_clock,
        };
        MCP2515_Handle h = NULL;
        ERROR_t rc = MCP2515_CreateOnBus(instances[i].host,
                                          &instances[i].bus_cfg,
                                          &instances[i].dev_cfg,
                                          instances[i].int_gpio,
                                          &cfg,
                                          &h);
        if (rc != ERROR_OK) {
            ESP_LOGE(TAG, "CreateOnBus failed for instance %u", (unsigned)i);
            mcp2515_multi_deinit();
            return false;
        }
        if (MCP2515_SetBitrate(h, instances[i].can_speed, instances[i].can_clock) != ERROR_OK) {
            ESP_LOGE(TAG, "SetBitrate failed for instance %u", (unsigned)i);
            mcp2515_multi_deinit();
            return false;
        }
        if (MCP2515_SetNormalMode(h) != ERROR_OK) {
            ESP_LOGE(TAG, "SetNormalMode failed for instance %u", (unsigned)i);
            mcp2515_multi_deinit();
            return false;
        }
        g_handles[i] = h;
    }

    g_count = count;
    ESP_LOGI(TAG, "Initialized %u MCP2515 instance(s)", (unsigned)g_count);
    return true;
}

bool mcp2515_multi_deinit(void)
{
    if (!g_handles) return true;
    for (size_t i=0; i<g_count; ++i) {
        if (g_handles[i]) {
            MCP2515_Destroy(g_handles[i]);
            g_handles[i] = NULL;
        }
    }
    free(g_handles);
    g_handles = NULL;
    g_count = 0;
    return true;
}

bool mcp2515_multi_send(size_t index, const twai_message_t* msg)
{
    if (!g_handles || index >= g_count || !msg) return false;
    CAN_FRAME f;
    to_frame(msg, &f);
    return MCP2515_SendMessageAfterCtrlCheck(g_handles[index], &f) == ERROR_OK;
}

bool mcp2515_multi_receive(size_t index, twai_message_t* msg)
{
    if (!g_handles || index >= g_count || !msg) return false;
    CAN_FRAME f;
    ERROR_t rc = MCP2515_ReadMessageAfterStatCheck(g_handles[index], &f);
    if (rc != ERROR_OK) return false;
    from_frame(&f, msg);
    return true;
}
