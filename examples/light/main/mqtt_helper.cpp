/* tls-mutual-auth example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "esp_system.h"
#include "mqtt_helper.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

static const char *TAG = "MQTT_HELPER";

/*
 * Prototypes for the demos that can be started from this project.  Note the
 * MQTT demo is not actually started until the network is already.
 */

esp_err_t mqtt_publish_to_topic(char *message, uint16_t size) 
{
    esp_err_t err = ESP_OK;

    err = publish_message_to_topic(message, size);

    if (err == EXIT_FAILURE) {
        err = ESP_FAIL;
    }
    return err;
}

void mqtt_init()
{
    ESP_LOGI(TAG, "[APP] Startup..");
    ESP_LOGI(TAG, "[APP] Free memory: %" PRIu32 " bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG, "[APP] IDF version: %s", esp_get_idf_version());

    esp_log_level_set("*", ESP_LOG_INFO);

    xTaskCreate(aws_iot_demo_main, "MQTT_Task", MQTT_TASK_STACK_SIZE, NULL, MQTT_TASK_PRIORITY, NULL);

    const char* taskName = pcTaskGetName(NULL);
    printf("MQTT helper: %s\n", taskName);
}
