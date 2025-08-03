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
#include <identify.h>
#include <identify_ids.h>
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

static const char *TAG = "identify_cluster";
constexpr uint16_t cluster_revision = 6;


namespace esp_matter {
namespace cluster {
namespace identify {


namespace attribute {
attribute_t *create_identify_time(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, IdentifyTime::Id, ATTRIBUTE_FLAG_WRITABLE | ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_identify_type(cluster_t *cluster, uint8_t value)
{
    return esp_matter::attribute::create(cluster, IdentifyType::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_enum8(value));
}

} /* attribute */


namespace command {
command_t *create_identify(cluster_t *cluster)
{
    return esp_matter::command::create(cluster, Identify::Id, COMMAND_FLAG_ACCEPTED, NULL);
}

command_t *create_trigger_effect(cluster_t *cluster)
{
    return esp_matter::command::create(cluster, TriggerEffect::Id, COMMAND_FLAG_ACCEPTED, NULL);
}

} /* command */



const function_generic_t *function_list = NULL;

const int function_flags = CLUSTER_FLAG_NONE;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags)
{
    cluster_t *cluster = esp_matter::cluster::create(endpoint, identify::Id, flags);
    VerifyOrReturnValue(cluster, NULL, ESP_LOGE(TAG, "Could not create cluster. cluster_id: 0x%08" PRIX32, identify::Id));
    if (flags & CLUSTER_FLAG_SERVER) {
        static const auto plugin_server_init_cb = CALL_ONCE(MatterIdentifyPluginServerInitCallback);
        set_plugin_server_init_callback(cluster, plugin_server_init_cb);
        add_function_list(cluster, function_list, function_flags);

        /* Attributes managed internally */
        global::attribute::create_feature_map(cluster, 0);

        /* Attributes not managed internally */
        global::attribute::create_cluster_revision(cluster, cluster_revision);

        attribute::create_identify_time(cluster, 0);
        attribute::create_identify_type(cluster, 0);

        command::create_identify(cluster);
        cluster::set_init_and_shutdown_callbacks(cluster, ESPMatterIdentifyClusterServerInitCallback,
                                                 ESPMatterIdentifyClusterServerShutdownCallback);
    }

    return cluster;
}

} /* identify */
} /* cluster */
} /* esp_matter */