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
#include <icd_management.h>
#include <icd_management_ids.h>
#include <binding.h>
#include <esp_matter_data_model_priv.h>
#include <app/ClusterCallbacks.h>

using namespace chip::app::Clusters;
using chip::app::CommandHandler;
using chip::app::DataModel::Decode;
using chip::TLV::TLVReader;
using namespace esp_matter;
using namespace esp_matter::cluster;
using namespace esp_matter::cluster::delegate_cb;

static const char *TAG = "icd_management_cluster";
constexpr uint16_t cluster_revision = 3;


namespace esp_matter {
namespace cluster {
namespace icd_management {

namespace feature {
namespace check_in_protocol_support {
uint32_t get_id()
{
    return CheckInProtocolSupport::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());
    attribute::create_registered_clients(cluster, NULL, 0, 0);
    attribute::create_icd_counter(cluster, 0);
    attribute::create_clients_supported_per_fabric(cluster, 1);
    attribute::create_maximum_check_in_backoff(cluster, 1);
    command::create_register_client(cluster);
    command::create_register_client_response(cluster);
    command::create_unregister_client(cluster);

    return ESP_OK;
}
} /* check_in_protocol_support */

namespace user_active_mode_trigger {
uint32_t get_id()
{
    return UserActiveModeTrigger::Id;
}

esp_err_t add(cluster_t *cluster, config_t *config)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());
    if (config) {
        attribute::create_user_active_mode_trigger_hint(cluster, config->user_active_mode_trigger_hint);
    } else {
        ESP_LOGE(TAG, "Config is NULL. Cannot add some attributes.");
    }

    return ESP_OK;
}
} /* user_active_mode_trigger */

namespace long_idle_time_support {
uint32_t get_id()
{
    return LongIdleTimeSupport::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());
    attribute::create_operating_mode(cluster, 0);
    command::create_stay_active_request(cluster);
    command::create_stay_active_response(cluster);

    return ESP_OK;
}
} /* long_idle_time_support */

namespace dynamic_sit_lit_support {
uint32_t get_id()
{
    return DynamicSitLitSupport::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());

    return ESP_OK;
}
} /* dynamic_sit_lit_support */

} /* feature */


namespace attribute {
attribute_t *create_idle_mode_duration(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, IdleModeDuration::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_active_mode_duration(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, ActiveModeDuration::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_active_mode_threshold(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, ActiveModeThreshold::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_registered_clients(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::check_in_protocol_support::get_id(), NULL);
    return esp_matter::attribute::create(cluster, RegisteredClients::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NONVOLATILE, esp_matter_array(value, length, count));
}

attribute_t *create_icd_counter(cluster_t *cluster, uint32_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::check_in_protocol_support::get_id(), NULL);
    return esp_matter::attribute::create(cluster, ICDCounter::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NONVOLATILE, esp_matter_uint32(value));
}

attribute_t *create_clients_supported_per_fabric(cluster_t *cluster, uint16_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::check_in_protocol_support::get_id(), NULL);
    return esp_matter::attribute::create(cluster, ClientsSupportedPerFabric::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_user_active_mode_trigger_hint(cluster_t *cluster, uint32_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::user_active_mode_trigger::get_id(), NULL);
    attribute_t *attribute = esp_matter::attribute::create(cluster, UserActiveModeTriggerHint::Id, ATTRIBUTE_FLAG_NONE, esp_matter_bitmap32(value));
    esp_matter::attribute::add_bounds(attribute, esp_matter_bitmap32(0), esp_matter_bitmap32(131071));
    return attribute;
}

attribute_t *create_user_active_mode_trigger_instruction(cluster_t *cluster, char *value, uint16_t length)
{
    VerifyOrReturnValue(length <= k_max_user_active_mode_trigger_instruction_length + 1, NULL, ESP_LOGE(TAG, "Could not create attribute, string length out of bound"));
    return esp_matter::attribute::create(cluster, UserActiveModeTriggerInstruction::Id, ATTRIBUTE_FLAG_NONE, esp_matter_char_str(value, length), k_max_user_active_mode_trigger_instruction_length + 1);
}

attribute_t *create_operating_mode(cluster_t *cluster, uint8_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::long_idle_time_support::get_id(), NULL);
    return esp_matter::attribute::create(cluster, OperatingMode::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_enum8(value));
}

attribute_t *create_maximum_check_in_backoff(cluster_t *cluster, uint32_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::check_in_protocol_support::get_id(), NULL);
    return esp_matter::attribute::create(cluster, MaximumCheckInBackoff::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

} /* attribute */


namespace command {
command_t *create_register_client(cluster_t *cluster)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::check_in_protocol_support::get_id(), NULL);
    return esp_matter::command::create(cluster, RegisterClient::Id, COMMAND_FLAG_ACCEPTED, NULL);
}

command_t *create_register_client_response(cluster_t *cluster)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::check_in_protocol_support::get_id(), NULL);
    return esp_matter::command::create(cluster, RegisterClientResponse::Id, COMMAND_FLAG_GENERATED, NULL);
}

command_t *create_unregister_client(cluster_t *cluster)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::check_in_protocol_support::get_id(), NULL);
    return esp_matter::command::create(cluster, UnregisterClient::Id, COMMAND_FLAG_ACCEPTED, NULL);
}

command_t *create_stay_active_request(cluster_t *cluster)
{
    return esp_matter::command::create(cluster, StayActiveRequest::Id, COMMAND_FLAG_ACCEPTED, NULL);
}

command_t *create_stay_active_response(cluster_t *cluster)
{
    return esp_matter::command::create(cluster, StayActiveResponse::Id, COMMAND_FLAG_GENERATED, NULL);
}

} /* command */



const function_generic_t *function_list = NULL;

const int function_flags = CLUSTER_FLAG_NONE;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags)
{
    cluster_t *cluster = esp_matter::cluster::create(endpoint, icd_management::Id, flags);
    VerifyOrReturnValue(cluster, NULL, ESP_LOGE(TAG, "Could not create cluster. cluster_id: 0x%08" PRIX32, icd_management::Id));
    if (flags & CLUSTER_FLAG_SERVER) {
        add_function_list(cluster, function_list, function_flags);

        /* Attributes managed internally */
        global::attribute::create_feature_map(cluster, 0);

        /* Attributes not managed internally */
        global::attribute::create_cluster_revision(cluster, cluster_revision);

        attribute::create_idle_mode_duration(cluster, 1);
        attribute::create_active_mode_duration(cluster, 300);
        attribute::create_active_mode_threshold(cluster, 300);

        cluster::set_init_and_shutdown_callbacks(cluster, ESPMatterIcdManagementClusterServerInitCallback,
                                                 ESPMatterIcdManagementClusterServerShutdownCallback);
    }

    return cluster;
}

} /* icd_management */
} /* cluster */
} /* esp_matter */