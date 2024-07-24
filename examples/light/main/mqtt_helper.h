#pragma once

#include "esp_log.h"
#include "esp_err.h"
#include "core_mqtt.h"

#define MQTT_TASK_STACK_SIZE 4096
#define MQTT_TASK_PRIORITY 1

extern void aws_iot_demo_main(void *pvParameters);

extern int publish_message_to_topic(char* message, uint16_t length);

void mqtt_init();

esp_err_t mqtt_publish_to_topic(char *message, uint16_t size);