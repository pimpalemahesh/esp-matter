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
#include <descriptor.h>
#include <descriptor_ids.h>
#include <binding.h>
#include <esp_matter_data_model_priv.h>
#include <app/ClusterCallbacks.h>

using namespace chip::app::Clusters;
using chip::app::CommandHandler;
using chip::app::DataModel::Decode;
using chip::TLV::TLVReader;
using namespace esp_matter;
using namespace esp_matter::cluster;
using namespace esp_matter::cluster::descriptor::feature;
using namespace esp_matter::cluster::descriptor::attribute;
using namespace esp_matter::cluster::delegate_cb;

static const char *TAG = "descriptor_cluster";
constexpr uint16_t cluster_revision = 3;

namespace esp_matter {
namespace cluster {
namespace descriptor {

namespace feature {
namespace tag_list {
uint32_t get_id()
{
    return TagList::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());
    attribute::create_tag_list(cluster, NULL, 0, 0);

    return ESP_OK;
}
} /* tag_list */

} /* feature */

namespace attribute {
attribute_t *create_device_type_list(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, DeviceTypeList::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_server_list(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, ServerList::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_client_list(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, ClientList::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_parts_list(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, PartsList::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_tag_list(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::tag_list::get_id(), NULL);
    return esp_matter::attribute::create(cluster, TagList::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_endpoint_unique_id(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, EndpointUniqueID::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

} /* attribute */

const function_generic_t *function_list = NULL;

const int function_flags = CLUSTER_FLAG_NONE;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags)
{
    cluster_t *cluster = esp_matter::cluster::create(endpoint, descriptor::Id, flags);
    VerifyOrReturnValue(cluster, NULL, ESP_LOGE(TAG, "Could not create cluster. cluster_id: 0x%08" PRIX32, descriptor::Id));
    if (flags & CLUSTER_FLAG_SERVER) {
        static const auto plugin_server_init_cb = CALL_ONCE(MatterDescriptorPluginServerInitCallback);
        set_plugin_server_init_callback(cluster, plugin_server_init_cb);
        add_function_list(cluster, function_list, function_flags);

        /* Attributes managed internally */
        global::attribute::create_feature_map(cluster, 0);

        /* Attributes not managed internally */
        global::attribute::create_cluster_revision(cluster, cluster_revision);

        attribute::create_device_type_list(cluster, NULL, 0, 0);
        attribute::create_server_list(cluster, NULL, 0, 0);
        attribute::create_client_list(cluster, NULL, 0, 0);
        attribute::create_parts_list(cluster, NULL, 0, 0);

        cluster::set_init_and_shutdown_callbacks(cluster, ESPMatterDescriptorClusterServerInitCallback,
                                                 ESPMatterDescriptorClusterServerShutdownCallback);
    }

    return cluster;
}

} /* descriptor */
} /* cluster */
} /* esp_matter */