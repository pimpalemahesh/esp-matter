// Copyright 2025 Espressif Systems (Shanghai) PTE LTD
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

/* THIS IS A GENERATED FILE, DO NOT EDIT */

#include <esp_log.h>
#include <esp_matter_core.h>
#include <esp_matter.h>

#include <app-common/zap-generated/cluster-enums.h>
#include <app-common/zap-generated/callback.h>
#include <app/InteractionModelEngine.h>
#include <zap_common/app/PluginApplicationCallbacks.h>
#include <app/clusters/mode-base-server/mode-base-cluster-objects.h>
#include <esp_matter_delegate_callbacks.h>
#include <water_tank_level_monitoring.h>
#include <water_tank_level_monitoring_ids.h>
#include <binding.h>
#include <esp_matter_data_model_priv.h>

using namespace chip::app::Clusters;
using chip::app::CommandHandler;
using chip::app::DataModel::Decode;
using chip::TLV::TLVReader;
using namespace esp_matter;
using namespace esp_matter::cluster;
using namespace esp_matter::cluster::water_tank_level_monitoring::feature;
using namespace esp_matter::cluster::water_tank_level_monitoring::attribute;
using namespace esp_matter::cluster::water_tank_level_monitoring::command;
using namespace esp_matter::cluster::delegate_cb;

static const char *TAG = "water_tank_level_monitoring_cluster";
constexpr uint16_t cluster_revision = 1;

namespace esp_matter {
namespace cluster {
namespace water_tank_level_monitoring {

namespace feature {
namespace condition {
uint32_t get_id()
{
    return Condition::Id;
}

esp_err_t add(cluster_t *cluster, config_t *config)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());
    if (config) {
        attribute::create_condition(cluster, config->condition);
        attribute::create_degradation_direction(cluster, config->degradation_direction);
    } else {
        ESP_LOGE(TAG, "Config is NULL. Cannot add some attributes.");
    }

    return ESP_OK;
}
} /* condition */

namespace warning {
uint32_t get_id()
{
    return Warning::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());

    return ESP_OK;
}
} /* warning */

namespace replacement_product_list {
uint32_t get_id()
{
    return ReplacementProductList::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());
    attribute::create_replacement_product_list(cluster, NULL, 0, 0);

    return ESP_OK;
}
} /* replacement_product_list */

} /* feature */

namespace attribute {
attribute_t *create_condition(cluster_t *cluster, uint8_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::condition::get_id(), NULL);
    attribute_t *attribute = esp_matter::attribute::create(cluster, Condition::Id, ATTRIBUTE_FLAG_NONE, esp_matter_uint8(value));
    esp_matter::attribute::add_bounds(attribute, esp_matter_uint8(0), esp_matter_uint8(254));
    return attribute;
}

attribute_t *create_degradation_direction(cluster_t *cluster, uint8_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::condition::get_id(), NULL);
    attribute_t *attribute = esp_matter::attribute::create(cluster, DegradationDirection::Id, ATTRIBUTE_FLAG_NONE, esp_matter_enum8(value));
    esp_matter::attribute::add_bounds(attribute, esp_matter_enum8(0), esp_matter_enum8(1));
    return attribute;
}

attribute_t *create_change_indication(cluster_t *cluster, uint8_t value)
{
    attribute_t *attribute = esp_matter::attribute::create(cluster, ChangeIndication::Id, ATTRIBUTE_FLAG_NONE, esp_matter_enum8(value));
    esp_matter::attribute::add_bounds(attribute, esp_matter_enum8(0), esp_matter_enum8(2));
    return attribute;
}

attribute_t *create_in_place_indicator(cluster_t *cluster, bool value)
{
    return esp_matter::attribute::create(cluster, InPlaceIndicator::Id, ATTRIBUTE_FLAG_NONE, esp_matter_bool(value));
}

attribute_t *create_last_changed_time(cluster_t *cluster, nullable<uint32_t> value)
{
    attribute_t *attribute = esp_matter::attribute::create(cluster, LastChangedTime::Id, ATTRIBUTE_FLAG_WRITABLE | ATTRIBUTE_FLAG_NULLABLE | ATTRIBUTE_FLAG_NONVOLATILE, esp_matter_nullable_uint32(value));
    esp_matter::attribute::add_bounds(attribute, esp_matter_nullable_uint32(0), esp_matter_nullable_uint32(65534));
    return attribute;
}

attribute_t *create_replacement_product_list(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::replacement_product_list::get_id(), NULL);
    return esp_matter::attribute::create(cluster, ReplacementProductList::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

} /* attribute */
namespace command {
command_t *create_reset_condition(cluster_t *cluster)
{
    return esp_matter::command::create(cluster, ResetCondition::Id, COMMAND_FLAG_ACCEPTED, NULL);
}

} /* command */

static void create_default_binding_cluster(endpoint_t *endpoint)
{
    binding::config_t config;
    binding::create(endpoint, &config, CLUSTER_FLAG_SERVER);
}

const function_generic_t *function_list = NULL;

const int function_flags = CLUSTER_FLAG_NONE;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags)
{
    cluster_t *cluster = esp_matter::cluster::create(endpoint, water_tank_level_monitoring::Id, flags);
    VerifyOrReturnValue(cluster, NULL, ESP_LOGE(TAG, "Could not create cluster. cluster_id: 0x%08" PRIX32, water_tank_level_monitoring::Id));
    if (flags & CLUSTER_FLAG_SERVER) {
        static const auto plugin_server_init_cb = CALL_ONCE(MatterWaterTankLevelMonitoringPluginServerInitCallback);
        set_plugin_server_init_callback(cluster, plugin_server_init_cb);
        add_function_list(cluster, function_list, function_flags);

        /* Attributes managed internally */
        global::attribute::create_feature_map(cluster, 0);

        /* Attributes not managed internally */
        global::attribute::create_cluster_revision(cluster, cluster_revision);

        if (config) {
            attribute::create_change_indication(cluster, config->change_indication);
        } else {
            ESP_LOGE(TAG, "Config is NULL. Cannot add some attributes.");
        }
    }

    if (flags & CLUSTER_FLAG_CLIENT) {
        create_default_binding_cluster(endpoint);
    }
    return cluster;
}

} /* water_tank_level_monitoring */
} /* cluster */
} /* esp_matter */