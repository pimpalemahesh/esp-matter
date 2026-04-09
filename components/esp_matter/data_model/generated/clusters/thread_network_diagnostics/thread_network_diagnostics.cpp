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

/* THIS IS A GENERATED FILE, DO NOT EDIT */

#include <esp_log.h>
#include <esp_matter_core.h>
#include <esp_matter.h>

#include <app-common/zap-generated/cluster-enums.h>
#include <app-common/zap-generated/callback.h>
#include <app/InteractionModelEngine.h>
#include <zap_common/app/PluginApplicationCallbacks.h>
#include <thread_network_diagnostics.h>
#include <thread_network_diagnostics_ids.h>
#include <binding.h>
#include <esp_matter_data_model_priv.h>

using namespace chip::app::Clusters;
using chip::app::CommandHandler;
using chip::app::DataModel::Decode;
using chip::TLV::TLVReader;
using namespace esp_matter;
using namespace esp_matter::cluster;
using namespace esp_matter::cluster::delegate_cb;

static const char *TAG = "thread_network_diagnostics_cluster";
constexpr uint16_t cluster_revision = 3;

static esp_err_t esp_matter_command_callback_reset_counts(const ConcreteCommandPath &command_path, TLVReader &tlv_data,
                                                          void *opaque_ptr)
{
    chip::app::Clusters::ThreadNetworkDiagnostics::Commands::ResetCounts::DecodableType command_data;
    CHIP_ERROR error = Decode(tlv_data, command_data);
    if (error == CHIP_NO_ERROR) {
        emberAfThreadNetworkDiagnosticsClusterResetCountsCallback((CommandHandler *)opaque_ptr, command_path, command_data);
    }
    return ESP_OK;
}

namespace esp_matter {
namespace cluster {
namespace thread_network_diagnostics {

namespace feature {
namespace packet_counts {
uint32_t get_id()
{
    return PacketCounts::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());

    return ESP_OK;
}
} /* packet_counts */

namespace error_counts {
uint32_t get_id()
{
    return ErrorCounts::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());
    attribute::create_overrun_count(cluster, 0);
    command::create_reset_counts(cluster);

    return ESP_OK;
}
} /* error_counts */

namespace mle_counts {
uint32_t get_id()
{
    return MLECounts::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());

    return ESP_OK;
}
} /* mle_counts */

namespace mac_counts {
uint32_t get_id()
{
    return MACCounts::Id;
}

esp_err_t add(cluster_t *cluster)
{
    VerifyOrReturnError(cluster, ESP_ERR_INVALID_ARG);
    update_feature_map(cluster, get_id());

    return ESP_OK;
}
} /* mac_counts */

} /* feature */

namespace attribute {
attribute_t *create_channel(cluster_t *cluster, nullable<uint16_t> value)
{
    return esp_matter::attribute::create(cluster, Channel::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint16(value));
}

attribute_t *create_routing_role(cluster_t *cluster, nullable<uint8_t> value)
{
    return esp_matter::attribute::create(cluster, RoutingRole::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_enum8(value));
}

attribute_t *create_network_name(cluster_t *cluster, char *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, NetworkName::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_char_str(value, length));
}

attribute_t *create_pan_id(cluster_t *cluster, nullable<uint16_t> value)
{
    return esp_matter::attribute::create(cluster, PanId::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint16(value));
}

attribute_t *create_extended_pan_id(cluster_t *cluster, nullable<uint64_t> value)
{
    return esp_matter::attribute::create(cluster, ExtendedPanId::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint64(value));
}

attribute_t *create_mesh_local_prefix(cluster_t *cluster, uint8_t *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, MeshLocalPrefix::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_octet_str(value, length));
}

attribute_t *create_overrun_count(cluster_t *cluster, uint64_t value)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::error_counts::get_id(), NULL);
    return esp_matter::attribute::create(cluster, OverrunCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint64(value));
}

attribute_t *create_neighbor_table(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, NeighborTable::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_route_table(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, RouteTable::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

attribute_t *create_partition_id(cluster_t *cluster, nullable<uint32_t> value)
{
    return esp_matter::attribute::create(cluster, PartitionId::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint32(value));
}

attribute_t *create_weighting(cluster_t *cluster, nullable<uint16_t> value)
{
    return esp_matter::attribute::create(cluster, Weighting::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint16(value));
}

attribute_t *create_data_version(cluster_t *cluster, nullable<uint16_t> value)
{
    return esp_matter::attribute::create(cluster, DataVersion::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint16(value));
}

attribute_t *create_stable_data_version(cluster_t *cluster, nullable<uint16_t> value)
{
    return esp_matter::attribute::create(cluster, StableDataVersion::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint16(value));
}

attribute_t *create_leader_router_id(cluster_t *cluster, nullable<uint8_t> value)
{
    return esp_matter::attribute::create(cluster, LeaderRouterId::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint8(value));
}

attribute_t *create_detached_role_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, DetachedRoleCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_child_role_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, ChildRoleCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_router_role_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, RouterRoleCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_leader_role_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, LeaderRoleCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_attach_attempt_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, AttachAttemptCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_partition_id_change_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, PartitionIdChangeCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_better_partition_attach_attempt_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, BetterPartitionAttachAttemptCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_parent_change_count(cluster_t *cluster, uint16_t value)
{
    return esp_matter::attribute::create(cluster, ParentChangeCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint16(value));
}

attribute_t *create_tx_total_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxTotalCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_unicast_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxUnicastCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_broadcast_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxBroadcastCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_ack_requested_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxAckRequestedCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_acked_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxAckedCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_no_ack_requested_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxNoAckRequestedCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_data_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxDataCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_data_poll_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxDataPollCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_beacon_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxBeaconCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_beacon_request_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxBeaconRequestCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_other_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxOtherCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_retry_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxRetryCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_direct_max_retry_expiry_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxDirectMaxRetryExpiryCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_indirect_max_retry_expiry_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxIndirectMaxRetryExpiryCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_err_cca_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxErrCcaCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_err_abort_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxErrAbortCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_tx_err_busy_channel_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, TxErrBusyChannelCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_total_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxTotalCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_unicast_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxUnicastCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_broadcast_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxBroadcastCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_data_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxDataCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_data_poll_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxDataPollCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_beacon_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxBeaconCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_beacon_request_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxBeaconRequestCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_other_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxOtherCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_address_filtered_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxAddressFilteredCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_dest_addr_filtered_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxDestAddrFilteredCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_duplicated_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxDuplicatedCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_err_no_frame_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxErrNoFrameCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_err_unknown_neighbor_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxErrUnknownNeighborCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_err_invalid_src_addr_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxErrInvalidSrcAddrCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_err_sec_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxErrSecCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_err_fcs_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxErrFcsCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_rx_err_other_count(cluster_t *cluster, uint32_t value)
{
    return esp_matter::attribute::create(cluster, RxErrOtherCount::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_uint32(value));
}

attribute_t *create_active_timestamp(cluster_t *cluster, nullable<uint64_t> value)
{
    return esp_matter::attribute::create(cluster, ActiveTimestamp::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint64(value));
}

attribute_t *create_pending_timestamp(cluster_t *cluster, nullable<uint64_t> value)
{
    return esp_matter::attribute::create(cluster, PendingTimestamp::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint64(value));
}

attribute_t *create_delay(cluster_t *cluster, nullable<uint32_t> value)
{
    return esp_matter::attribute::create(cluster, Delay::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_nullable_uint32(value));
}

attribute_t *create_security_policy(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, SecurityPolicy::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_array(value, length, count));
}

attribute_t *create_channel_page_0_mask(cluster_t *cluster, uint8_t *value, uint16_t length)
{
    return esp_matter::attribute::create(cluster, ChannelPage0Mask::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_octet_str(value, length));
}

attribute_t *create_operational_dataset_components(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, OperationalDatasetComponents::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY | ATTRIBUTE_FLAG_NULLABLE, esp_matter_array(value, length, count));
}

attribute_t *create_active_network_faults_list(cluster_t *cluster, uint8_t *value, uint16_t length, uint16_t count)
{
    return esp_matter::attribute::create(cluster, ActiveNetworkFaultsList::Id, ATTRIBUTE_FLAG_MANAGED_INTERNALLY, esp_matter_array(value, length, count));
}

} /* attribute */
namespace command {
command_t *create_reset_counts(cluster_t *cluster)
{
    uint32_t feature_map = get_feature_map_value(cluster);
    VerifyOrReturnValue(feature_map & feature::error_counts::get_id(), NULL);
    return esp_matter::command::create(cluster, ResetCounts::Id, COMMAND_FLAG_ACCEPTED, esp_matter_command_callback_reset_counts);
}

} /* command */

namespace event {
event_t *create_connection_status(cluster_t *cluster)
{
    return esp_matter::event::create(cluster, ConnectionStatus::Id);
}

event_t *create_network_fault_change(cluster_t *cluster)
{
    return esp_matter::event::create(cluster, NetworkFaultChange::Id);
}

} /* event */

const function_generic_t *function_list = NULL;

const int function_flags = CLUSTER_FLAG_NONE;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags)
{
    cluster_t *cluster = esp_matter::cluster::create(endpoint, thread_network_diagnostics::Id, flags);
    VerifyOrReturnValue(cluster, NULL, ESP_LOGE(TAG, "Could not create cluster. cluster_id: 0x%08" PRIX32, thread_network_diagnostics::Id));
    if (flags & CLUSTER_FLAG_SERVER) {
        static const auto plugin_server_init_cb = CALL_ONCE(MatterThreadNetworkDiagnosticsPluginServerInitCallback);
        set_plugin_server_init_callback(cluster, plugin_server_init_cb);
        add_function_list(cluster, function_list, function_flags);

        /* Attributes managed internally */
        global::attribute::create_feature_map(cluster, 0);

        /* Attributes not managed internally */
        global::attribute::create_cluster_revision(cluster, cluster_revision);

        attribute::create_channel(cluster, 0);
        attribute::create_routing_role(cluster, 0);
        attribute::create_network_name(cluster, NULL, 0);
        attribute::create_pan_id(cluster, 0);
        attribute::create_extended_pan_id(cluster, 0);
        attribute::create_mesh_local_prefix(cluster, NULL, 0);
        attribute::create_neighbor_table(cluster, NULL, 0, 0);
        attribute::create_route_table(cluster, NULL, 0, 0);
        attribute::create_partition_id(cluster, 0);
        attribute::create_weighting(cluster, 0);
        attribute::create_data_version(cluster, 0);
        attribute::create_stable_data_version(cluster, 0);
        attribute::create_leader_router_id(cluster, 0);
        attribute::create_security_policy(cluster, NULL, 0, 0);
        attribute::create_channel_page_0_mask(cluster, NULL, 0);
        attribute::create_operational_dataset_components(cluster, NULL, 0, 0);
        attribute::create_active_network_faults_list(cluster, NULL, 0, 0);
    }

    return cluster;
}

} /* thread_network_diagnostics */
} /* cluster */
} /* esp_matter */
