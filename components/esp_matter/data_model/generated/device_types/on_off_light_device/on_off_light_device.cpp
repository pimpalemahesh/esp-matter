// Copyright 2026 Espressif Systems (Shanghai) PTE LTD
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/* This is a Generated File */

#include <esp_log.h>
#include <esp_matter.h>
#include <esp_matter_core.h>
#include <on_off_light_device.h>

using namespace esp_matter;
using namespace esp_matter::cluster;
using namespace esp_matter::endpoint;

namespace esp_matter {
namespace endpoint {
namespace on_off_light {
uint32_t get_device_type_id()
{
    return ESP_MATTER_ON_OFF_LIGHT_DEVICE_TYPE_ID;
}

uint8_t get_device_type_version()
{
    return ESP_MATTER_ON_OFF_LIGHT_DEVICE_TYPE_VERSION;
}

endpoint_t *create(node_t *node, config_t *config, uint8_t flags, void *priv_data)
{
    endpoint_t *endpoint = esp_matter::endpoint::create(node, flags, priv_data);
    VerifyOrReturnValue(endpoint != nullptr, NULL, ESP_LOGE("on_off_light", "Failed to create endpoint"));

    cluster_t *descriptor_cluster = descriptor::create(endpoint, &(config->descriptor), CLUSTER_FLAG_SERVER);
    VerifyOrReturnValue(descriptor_cluster != nullptr, NULL, ESP_LOGE("on_off_light", "Failed to create descriptor cluster"));

    VerifyOrReturnValue(add(endpoint, config) == ESP_OK, NULL, ESP_LOGE("on_off_light", "Failed to add device type"));
    return endpoint;
}

esp_err_t add(endpoint_t *endpoint, config_t *config)
{
    esp_err_t err = add_device_type(endpoint, get_device_type_id(), get_device_type_version());
    VerifyOrReturnError(err == ESP_OK, err);

    cluster_t *identify = cluster::identify::create(endpoint, &(config->identify), CLUSTER_FLAG_SERVER);
    cluster::identify::command::create_trigger_effect(identify);
    cluster::groups::create(endpoint, &(config->groups), CLUSTER_FLAG_SERVER);
    cluster_t *on_off = cluster::on_off::create(endpoint, &(config->on_off), CLUSTER_FLAG_SERVER);
    cluster::on_off::feature::lighting::add(on_off, &(config->on_off_lighting));
    cluster_t *scenes_management = cluster::scenes_management::create(endpoint, &(config->scenes_management), CLUSTER_FLAG_SERVER);
    cluster::scenes_management::command::create_copy_scene(scenes_management);
    return ESP_OK;
}

} /* on_off_light */
} /* endpoint */
} /* esp_matter */
