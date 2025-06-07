#include <stddef.h>
#include <limits.h>
#include "esp_timer.h"
#include "esp_log.h"
#include "examples_utils.h"

#define TAG "EXAMPLES_UTILS"

// store 48 least significant bits of 64bit value into 6B array (big-endian)
void store_timestamp48(uint64_t source, unit48_big_endian_t *target_ptr)
{
    for (int i = 0; i < 6; ++i)
        (*target_ptr)[5 - i] = (source >> (i * 8)) & 0xFF;
}

// restore 6B big-endian timestamp back to 64bit value
uint64_t restore_timestamp48(const unit48_big_endian_t *src_ptr)
{
    uint64_t result = 0;
    for (int i = 0; i < 6; ++i)
        result = (result << 8) | (*src_ptr)[i];
    return result;
}

void fullfill_test_messages(uint8_t sender_id, uint8_t heartbeat, can_message_t *message) 
{
    if (message == NULL) {
        ESP_LOGE(TAG, "Invalid frame pointer");
        return;
    }

    // view to message->data (8 bytes) as a test_can_message_t
    test_can_message_t * payload = (test_can_message_t *)message->data;

    message->id = TEST_MSG_ID;
    message->extended_id = false;
    message->rtr = false;
    message->dlc = 8;
    payload->sender_id = sender_id;
    payload->heartbeat = heartbeat;
    store_timestamp48(esp_timer_get_time(), & (payload->timestamp));
} // get_test_messages

void print_can_message(const can_message_t *message) {
    if (message == NULL) {
        ESP_LOGE(TAG, "Invalid frame pointer");
        return;
    }
    
    printf("CAN message ID: %lu\n", message->id);
    switch (message->id) {
        case TEST_MSG_ID:
            // view payload as test_can_message_t
            test_can_message_t *payload1 = (test_can_message_t *)message->data;

            printf("Test message\n");
            printf("Sender ID: %u\n", payload1->sender_id);
            printf("Heartbeat: %u\n", payload1->heartbeat);
            printf("Timestamp: %llu [us]\n", restore_timestamp48(& (payload1->timestamp)));
            break;

        case CAN_MSG_WITH_TWO_UINT32_ID:
            // view payload as can_message_with_two_uint32_t
            can_message_with_two_uint32_t *payload2 = (can_message_with_two_uint32_t *)message->data;
            printf("Two uint32 message\n");
            printf("Value uint32_1: %lu\n", payload2->value_uint32_1);
            printf("Value uint32_2: %lu\n", payload2->value_uint32_2);
            break;

        case CAN_MSG_WITH_ONE_UINT64_ID:
            // view payload as can_message_with_one_uint64_t
            can_message_with_one_uint64_t *payload3 = (can_message_with_one_uint64_t *)message->data;

            printf("One uint64 message\n");
            printf("Value uint64: %llu\n", payload3->value_uint64);
            break;

        case EIGHT_BYTES_ARRAY_MESSAGE_ID:
            // view payload as eight_bytes_array_message_t
            eight_bytes_array_message_t *payload4 = (eight_bytes_array_message_t *)message->data;

            printf("Eight bytes array message\n");
            printf("Data:");
            for (int i = 0; i < 8; i++) {
                printf(" %02X", payload4->data[i]);
            }
            printf("\n");
            break;

        default:
            printf("Unknown message ID: %lu\n", message->id);
            break;
    }
        // debug print message->data
    printf("message->data (dec):|");
    for (int i = 0; i < message->dlc; i++) {
        printf("%03d|", message->data[i]);
    }
    printf("\n");
}

// --- latency statistic --------------------------------------------------------------------------
void reset_latency_statistic(latency_statistic_t *statistic_ptr)
{
    statistic_ptr->time_shift_us = 0;
    statistic_ptr->latency_us_sum = 0;
    statistic_ptr->latency_us_count = 0;
    statistic_ptr->latency_us_min = LONG_MAX;
    statistic_ptr->latency_us_max = LONG_MIN;
}

void update_latency_statistic(latency_statistic_t *statistic_ptr, uint64_t sender_timestamp_us) 
{
    if (statistic_ptr->time_shift_us == 0) {
        // count time shift between sender and receiver from first message
        statistic_ptr->time_shift_us = esp_timer_get_time() - sender_timestamp_us;
    }
    // calculate latency from sender timestamp and time shift
    uint64_t latency_us = esp_timer_get_time() - sender_timestamp_us + statistic_ptr->time_shift_us;
    statistic_ptr->latency_us_sum += latency_us;
    statistic_ptr->latency_us_count++;
    if (latency_us < statistic_ptr->latency_us_min) {
        statistic_ptr->latency_us_min = latency_us;
    } else if (latency_us > statistic_ptr->latency_us_max) {
        statistic_ptr->latency_us_max = latency_us;
    }
}

void print_latency_statisti(latency_statistic_t *statistic_ptr)
{
    ESP_LOGI(TAG, "Latency statistic:");
    ESP_LOGI(TAG, "Count of messages: %llu", statistic_ptr->latency_us_count);
    ESP_LOGI(TAG, "Latency min: %ld [us]", statistic_ptr->latency_us_min);
    ESP_LOGI(TAG, "Latency max: %ld [us]", statistic_ptr->latency_us_max);
    if (statistic_ptr->latency_us_count > 0) {
        ESP_LOGI(TAG, "Latency average: %ld [us]", statistic_ptr->latency_us_sum / (long int)statistic_ptr->latency_us_count);
    } else {
        ESP_LOGI(TAG, "Latency average: N/A");
    }
}

bool check_heartbeat(uint8_t received_heartbeat, uint8_t *expected_heartbeat_ptr)
{
    bool success = received_heartbeat == *expected_heartbeat_ptr;
    if (!success) {
        ESP_LOGE(TAG, "Heartbeat mismatch: expected %u, received %u", *expected_heartbeat_ptr, received_heartbeat);
    } 
    // add 1 to expected_heartbeat_ptr
    *expected_heartbeat_ptr = (received_heartbeat + 1) % 255;
    
    return success;
}

uint8_t next_heartbeat(const uint8_t heartbeat) {
    return (heartbeat + 1) % 255;
}

static uint32_t received_index = 0;
static uint32_t send_index = 0;
#define MAX_RS_INDEX 10000
#define MAX_RS_INDEX_ON_ONE_LINE 80

void process_received_message(can_message_t *message, latency_statistic_t *statistic_ptr, uint8_t *expected_heartbeat_ptr, const bool print_during_receive) {
    if (message == NULL) {
        ESP_LOGE(TAG, "Invalid message pointer");
        return;
    }
    if (statistic_ptr == NULL) {
        ESP_LOGE(TAG, "Invalid statistic pointer");
        return;
    }
    if (expected_heartbeat_ptr == NULL) {
        ESP_LOGE(TAG, "Invalid expected heartbeat pointer");
        return;
    }
    if (print_during_receive) {
        print_can_message(message);
    } else {
        if (received_index % MAX_RS_INDEX_ON_ONE_LINE == 0) {
            printf("\n<-\n");
            fflush(stdout);
        }
        printf(".");
        received_index++;
        if (received_index >= MAX_RS_INDEX) {
            received_index = 0;
        }
    }
    if (message->id == TEST_MSG_ID) {
        test_can_message_t *payload = (test_can_message_t *)message->data;
        // if (!check_heartbeat(payload->heartbeat, expected_heartbeat_ptr)) {
        //     return;
        // }
        update_latency_statistic(statistic_ptr, restore_timestamp48(& (payload->timestamp)));

        if (payload->sender_id == END_TAG_ID) {
            print_latency_statisti(statistic_ptr);
            reset_latency_statistic(statistic_ptr);
        }
    } 
}

void debug_send_message(can_message_t *message, const bool print_during_send) {
    if (message == NULL) {
        ESP_LOGE(TAG, "Invalid frame pointer");
        return;
    }
    if (print_during_send) {
        print_can_message(message);
    } else {
        if (send_index % MAX_RS_INDEX_ON_ONE_LINE == 0) {
            printf("\n->\n");
            fflush(stdout);
        }
        printf(".");
        send_index++;
        if (send_index >= MAX_RS_INDEX) {
            send_index = 0;
        }
    }
}