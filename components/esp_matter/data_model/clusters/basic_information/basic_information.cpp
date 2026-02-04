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
#include <basic_information.h>
#include <basic_information_ids.h>
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

static const char *TAG = "basic_information_cluster";
constexpr uint16_t cluster_revision = 5;

namespace esp_matter {
namespace cluster {
namespace basic_information {

namespace attribute {
attribute_t *create_data_model_revision(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, DataModelRevision::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_vendor_name(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, VendorName::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_vendor_id(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, VendorID::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_product_name(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, ProductName::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_product_id(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, ProductID::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_node_label(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, NodeLabel::Id, ATTRIBUTE_FLAG_WRITABLE | ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NONVOLATILE, esp_matter_char_str(value, length));
}

attribute_t *create_location(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, Location::Id, ATTRIBUTE_FLAG_WRITABLE | ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NONVOLATILE, esp_matter_char_str(value, length));
}

attribute_t *create_hardware_version(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, HardwareVersion::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_hardware_version_string(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, HardwareVersionString::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_software_version(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, SoftwareVersion::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_software_version_string(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, SoftwareVersionString::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_manufacturing_date(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, ManufacturingDate::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_part_number(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, PartNumber::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_product_url(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, ProductURL::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_product_label(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, ProductLabel::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_serial_number(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, SerialNumber::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_local_config_disabled(cluster_t *cluster, bool value)
{
    return esp_matter::attribute::create(cluster, LocalConfigDisabled::Id, ATTRIBUTE_FLAG_WRITABLE | ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NONVOLATILE, esp_matter_bool(value));
}

attribute_t *create_reachable(cluster_t *cluster, bool value)
{
    return esp_matter::attribute::create(cluster, Reachable::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_bool(value));
}

attribute_t *create_unique_id(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, UniqueID::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_char_str(value, length));
}

attribute_t *create_capability_minima(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, CapabilityMinima::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_product_appearance(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, ProductAppearance::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_specification_version(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, SpecificationVersion::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_max_paths_per_invoke(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, MaxPathsPerInvoke::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

} /* attribute */

namespace event {
event_t *create_start_up(cluster_t *cluster)
{
    return esp_matter::event::create(cluster, StartUp::Id);
}

event_t *create_shut_down(cluster_t *cluster)
{
    return esp_matter::event::create(cluster, ShutDown::Id);
}

event_t *create_leave(cluster_t *cluster)
{
    return esp_matter::event::create(cluster, Leave::Id);
}

event_t *create_reachable_changed(cluster_t *cluster)
{
    VerifyOrReturnValue(esp_matter::attribute::get(cluster, 0x0011) != nullptr, NULL);
    return esp_matter::event::create(cluster, ReachableChanged::Id);
}

} /* event */

const function_generic_t *function_list = NULL;

const int function_flags = CLUSTER_FLAG_NONE;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags)
{
    cluster_t *cluster = esp_matter::cluster::create(endpoint, basic_information::Id, flags);
    VerifyOrReturnValue(cluster, NULL, ESP_LOGE(TAG, "Could not create cluster. cluster_id: 0x%08" PRIX32, basic_information::Id));
    if (flags & CLUSTER_FLAG_SERVER) {
        static const auto plugin_server_init_cb = CALL_ONCE(MatterBasicInformationPluginServerInitCallback);
        set_plugin_server_init_callback(cluster, plugin_server_init_cb);
        add_function_list(cluster, function_list, function_flags);

        /* Attributes managed internally */
        global::attribute::create_feature_map(cluster, 0);

        /* Attributes not managed internally */
        global::attribute::create_cluster_revision(cluster, cluster_revision);

        attribute::create_data_model_revision(cluster, 0);
        attribute::create_vendor_name(cluster, NULL, 0);
        attribute::create_vendor_id(cluster, 0);
        attribute::create_product_name(cluster, NULL, 0);
        attribute::create_product_id(cluster, 0);
        attribute::create_node_label(cluster, NULL, 0);
        attribute::create_location(cluster, NULL, 0);
        attribute::create_hardware_version(cluster, 0);
        attribute::create_hardware_version_string(cluster, NULL, 0);
        attribute::create_software_version(cluster, 0);
        attribute::create_software_version_string(cluster, NULL, 0);
        attribute::create_unique_id(cluster, NULL, 0);
        attribute::create_capability_minima(cluster, NULL, 0, 0);
        attribute::create_specification_version(cluster, 0);
        attribute::create_max_paths_per_invoke(cluster, 1);
        /* Events */
        event::create_start_up(cluster);

        cluster::set_init_and_shutdown_callbacks(cluster, ESPMatterBasicInformationClusterServerInitCallback,
                                                 ESPMatterBasicInformationClusterServerShutdownCallback);
    }

    return cluster;
}

} /* basic_information */
} /* cluster */
} /* esp_matter */