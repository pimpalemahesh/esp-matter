#include <stdio.h>
#include <string.h>
#include <sdkconfig.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_log.h>
#include <esp_err.h>
#include <mqtt_client.h>
#include <esp_event.h>
#include <include/app_mqtt_glue.h>
#include <include/esp_utils.h>
#include <esp_idf_version.h>

static const char *TAG = "esp_mqtt_glue";

#define MAX_MQTT_SUBSCRIPTIONS 20
#define CONFIG_ESP_MQTT_KEEP_ALIVE_INTERVAL 100

typedef struct {
    char *topic;
    esp_mqtt_subscribe_cb_t cb;
    void *priv;
} esp_mqtt_glue_subscription_t;

typedef struct {
    esp_mqtt_client_handle_t mqtt_client;
    esp_mqtt_conn_params_t *conn_params;
    esp_mqtt_glue_subscription_t *subscriptions[MAX_MQTT_SUBSCRIPTIONS];
} esp_mqtt_glue_data_t;
esp_mqtt_glue_data_t *mqtt_data;

typedef struct {
    char *data;
    char *topic;
} esp_mqtt_glue_long_data_t;

static void esp_mqtt_glue_deinit(void);

static void esp_mqtt_glue_subscribe_callback(const char *topic, int topic_len, const char *data, int data_len)
{
    esp_mqtt_glue_subscription_t **subscriptions = mqtt_data->subscriptions;
    int i;
    for (i = 0; i < MAX_MQTT_SUBSCRIPTIONS; i++) {
        if (subscriptions[i]) {
            if ((strncmp(topic, subscriptions[i]->topic, topic_len) == 0)
                    && (topic_len == strlen(subscriptions[i]->topic))) {
                subscriptions[i]->cb(subscriptions[i]->topic, (void *)data, data_len, subscriptions[i]->priv);
            }
        }
    }
}

static esp_err_t esp_mqtt_glue_subscribe(const char *topic, esp_mqtt_subscribe_cb_t cb, uint8_t qos, void *priv_data)
{
    if (!mqtt_data || !topic || !cb) {
        return ESP_FAIL;
    }
    int i;
    for (i = 0; i < MAX_MQTT_SUBSCRIPTIONS; i++) {
        if (!mqtt_data->subscriptions[i]) {
            esp_mqtt_glue_subscription_t *subscription = (esp_mqtt_glue_subscription_t*)calloc(1, sizeof(esp_mqtt_glue_subscription_t));
            if (!subscription) {
                return ESP_FAIL;
            }
            subscription->topic = strdup(topic);
            if (!subscription->topic) {
                free(subscription);
                return ESP_FAIL;
            }
            int ret = esp_mqtt_client_subscribe(mqtt_data->mqtt_client, subscription->topic, qos);
            if (ret < 0) {
                free(subscription->topic);
                free(subscription);
                return ESP_FAIL;
            }
            subscription->priv = priv_data;
            subscription->cb = cb;
            mqtt_data->subscriptions[i] = subscription;
            ESP_LOGD(TAG, "Subscribed to topic: %s", topic);
            return ESP_OK;
        }
    }
    return ESP_FAIL;
}

static void unsubscribe_helper(esp_mqtt_glue_subscription_t **subscription)
{
    if (subscription && *subscription) {
        if (esp_mqtt_client_unsubscribe(mqtt_data->mqtt_client, (*subscription)->topic) < 0) {
            ESP_LOGW(TAG, "Could not unsubscribe from topic: %s", (*subscription)->topic);
        }
        free((*subscription)->topic);
        free(*subscription);
        *subscription = NULL;
    }
}

static esp_err_t esp_mqtt_glue_unsubscribe(const char *topic)
{
    if (!mqtt_data || !topic) {
        return ESP_FAIL;
    }
    esp_mqtt_glue_subscription_t **subscriptions = mqtt_data->subscriptions;
    int i;
    for (i = 0; i < MAX_MQTT_SUBSCRIPTIONS; i++) {
        if (subscriptions[i]) {
            if (strncmp(topic, subscriptions[i]->topic, strlen(topic)) == 0) {
                unsubscribe_helper(&subscriptions[i]);
                return ESP_OK;
            }
        }
    }
    return ESP_FAIL;
}

static esp_err_t esp_mqtt_glue_publish(const char *topic, void *data, size_t data_len, uint8_t qos, int *msg_id)
{
    if (!mqtt_data || !topic || !data) {
        return ESP_FAIL;
    }
    ESP_LOGD(TAG, "Publishing to %s", topic);
    int ret = esp_mqtt_client_publish(mqtt_data->mqtt_client, topic, (const char*)data, data_len, qos, 0);
    if (ret < 0) {
        ESP_LOGE(TAG, "MQTT Publish failed");
        return ESP_FAIL;
    }
    if (msg_id) {
        *msg_id = ret;
    }
    return ESP_OK;
}

static esp_mqtt_glue_long_data_t *esp_mqtt_glue_free_long_data(esp_mqtt_glue_long_data_t *long_data)
{
    if (long_data) {
        if (long_data->topic) {
            free(long_data->topic);
        }
        if (long_data->data) {
            free(long_data->data);
        }
        free(long_data);
    }
    return NULL;
}

static esp_mqtt_glue_long_data_t *esp_mqtt_glue_manage_long_data(esp_mqtt_glue_long_data_t *long_data,
        esp_mqtt_event_handle_t event)
{
    if (event->topic) {
        /* This is new data. Free any earlier data, if present. */
        esp_mqtt_glue_free_long_data(long_data);
        long_data = (esp_mqtt_glue_long_data_t*)calloc(1, sizeof(esp_mqtt_glue_long_data_t));
        if (!long_data) {
            ESP_LOGE(TAG, "Could not allocate memory for esp_mqtt_glue_long_data_t");
            return NULL;
        }
        long_data->data = (char*)MEM_CALLOC_EXTRAM(1, event->total_data_len);
        if (!long_data->data) {
            ESP_LOGE(TAG, "Could not allocate %d bytes for received data.", event->total_data_len);
            return esp_mqtt_glue_free_long_data(long_data);
        }
        long_data->topic = strndup(event->topic, event->topic_len);
        if (!long_data->topic) {
            ESP_LOGE(TAG, "Could not allocate %d bytes for received topic.", event->topic_len);
            return esp_mqtt_glue_free_long_data(long_data);
        }
    }
    if (long_data) {
        memcpy(long_data->data + event->current_data_offset, event->data, event->data_len);

        if ((event->current_data_offset + event->data_len) == event->total_data_len) {
            esp_mqtt_glue_subscribe_callback(long_data->topic, strlen(long_data->topic),
                        long_data->data, event->total_data_len);
            return esp_mqtt_glue_free_long_data(long_data);
        }
    }
    return long_data;
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t)event_data;

    switch (event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "MQTT Connected");
            /* Resubscribe to all topics after reconnection */
            for (int i = 0; i < MAX_MQTT_SUBSCRIPTIONS; i++) {
                if (mqtt_data->subscriptions[i]) {
                    esp_mqtt_client_subscribe(event->client, mqtt_data->subscriptions[i]->topic, 1);
                }
            }
            break;
        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGW(TAG, "MQTT Disconnected. Will try reconnecting in a while...");
            break;

        case MQTT_EVENT_SUBSCRIBED:
            ESP_LOGD(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
            break;
        case MQTT_EVENT_UNSUBSCRIBED:
            ESP_LOGD(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
            break;
        case MQTT_EVENT_PUBLISHED:
            ESP_LOGD(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
            break;
        case MQTT_EVENT_DATA: {
            ESP_LOGD(TAG, "MQTT_EVENT_DATA");
            static esp_mqtt_glue_long_data_t *long_data;
            /* Topic can be NULL, for data longer than the MQTT buffer */
            if (event->topic) {
                ESP_LOGD(TAG, "TOPIC=%.*s\r\n", event->topic_len, event->topic);
            }
            ESP_LOGD(TAG, "DATA=%.*s\r\n", event->data_len, event->data);
            if (event->data_len == event->total_data_len) {
                if (long_data) {
                    long_data = esp_mqtt_glue_free_long_data(long_data);
                }
                esp_mqtt_glue_subscribe_callback(event->topic, event->topic_len, event->data, event->data_len);
            } else {
                long_data = esp_mqtt_glue_manage_long_data(long_data, event);
            }
            break;
        }
        case MQTT_EVENT_ERROR:
            ESP_LOGE(TAG, "MQTT_EVENT_ERROR");
            break;
        default:
            ESP_LOGD(TAG, "Other event id:%d", event->event_id);
            break;
    }
}

static esp_err_t esp_mqtt_glue_connect(void)
{
    if (!mqtt_data) {
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "Connecting to %s", mqtt_data->conn_params->mqtt_host);
    esp_err_t ret = esp_mqtt_client_start(mqtt_data->mqtt_client);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_mqtt_client_start() failed with err = %d", ret);
        return ret;
    }
    return ESP_OK;
}

static void esp_mqtt_glue_unsubscribe_all(void)
{
    if (!mqtt_data) {
        return;
    }
    int i;
    for (i = 0; i < MAX_MQTT_SUBSCRIPTIONS; i++) {
        if (mqtt_data->subscriptions[i]) {
            unsubscribe_helper(&(mqtt_data->subscriptions[i]));
        }
    }
}

static esp_err_t esp_mqtt_glue_disconnect(void)
{
    if (!mqtt_data) {
        return ESP_FAIL;
    }
    esp_mqtt_glue_unsubscribe_all();
    esp_err_t err = esp_mqtt_client_stop(mqtt_data->mqtt_client);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Failed to disconnect from MQTT");
    } else {
        ESP_LOGI(TAG, "MQTT Disconnected.");
    }
    return err;
}

// Dummy implementation of esp_crt_bundle_attach
esp_err_t esp_crt_bundle_attach(void *client) {
    return ESP_OK; // Just a dummy function for testing purposes
}

static esp_err_t esp_mqtt_glue_init(esp_mqtt_conn_params_t *conn_params)
{
    if (mqtt_data) {
        ESP_LOGE(TAG, "MQTT already initialized");
        return ESP_OK;
    }
    if (!conn_params) {
        ESP_LOGE(TAG, "Connection params are mandatory for esp_mqtt_glue_init");
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "Initialising MQTT");
    mqtt_data = (esp_mqtt_glue_data_t*)calloc(1, sizeof(esp_mqtt_glue_data_t));
    if (!mqtt_data) {
        ESP_LOGE(TAG, "Failed to allocate memory for esp_mqtt_glue_data_t");
        return ESP_ERR_NO_MEM;
    }
    mqtt_data->conn_params = conn_params;


    const esp_mqtt_client_config_t mqtt_client_cfg = {
        .broker = {
            .address = {
                .hostname = conn_params->mqtt_host,  // Correct field order: hostname first
                .transport = MQTT_TRANSPORT_OVER_SSL, // Transport after port
                .port = 8883,                        // Port for SSL
            },
            .verification = {
                .crt_bundle_attach = esp_crt_bundle_attach,  // Use dummy function
            },
        },
        .credentials = {
            .client_id = (const char *)conn_params->client_id,  // Client ID
        },
        .session = {
            .keepalive = CONFIG_ESP_MQTT_KEEP_ALIVE_INTERVAL,  // Keepalive interval
        },
    };

    mqtt_data->mqtt_client = esp_mqtt_client_init(&mqtt_client_cfg);
    if (!mqtt_data->mqtt_client) {
        ESP_LOGE(TAG, "esp_mqtt_client_init failed");
        esp_mqtt_glue_deinit();
        return ESP_FAIL;
    }
    esp_mqtt_client_register_event(mqtt_data->mqtt_client, MQTT_EVENT_ANY, mqtt_event_handler, mqtt_data->mqtt_client);

    return esp_mqtt_glue_connect();
}

static void esp_mqtt_glue_deinit(void)
{
    if (mqtt_data) {
        esp_mqtt_glue_disconnect();
        free(mqtt_data);
        mqtt_data = NULL;
    }
}

esp_err_t esp_mqtt_glue_setup(esp_mqtt_config_t *mqtt_config)
{
    mqtt_config->init           = esp_mqtt_glue_init;
    mqtt_config->deinit         = esp_mqtt_glue_deinit;
    mqtt_config->connect        = esp_mqtt_glue_connect;
    mqtt_config->disconnect     = esp_mqtt_glue_disconnect;
    mqtt_config->publish        = esp_mqtt_glue_publish;
    mqtt_config->subscribe      = esp_mqtt_glue_subscribe;
    mqtt_config->unsubscribe    = esp_mqtt_glue_unsubscribe;
    mqtt_config->setup_done     = true;
    return ESP_OK;
}
