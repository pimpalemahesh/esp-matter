# Copyright 2026 Espressif Systems (Shanghai) PTE LTD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Dict, FrozenSet, List

COMMAND_CALLBACK_SKIP: FrozenSet[str] = frozenset(
    [
        "bridged_device_basic_information",
    ]
)

DELEGATE_CALLBACK_SKIP: FrozenSet[str] = frozenset(
    [
        "camera_av_settings_user_level_management",
        "camera_av_stream_management",
        "webrtc_transport_provider",
        "webrtc_transport_requestor",
        "tls_certificate_management",
        "tls_client_management",
        "zone_management",
    ]
)

# TODO: To be removed once the delegate callback is present in the codebase
# connectedhomeip/src/app/clusters/mode-select/
DELEGATE_CALLBACK_INCLUDE: FrozenSet[str] = frozenset(
    [
        "mode_select",
    ]
)

PLUGIN_CALLBACK_SKIP: FrozenSet[str] = frozenset(
    [
        "icd_management",
    ]
)


# List of command callbacks to skip
CALLBACK_STUB_SKIP: FrozenSet[str] = frozenset()

CLUSTER_NAME_OVERRIDES: Dict[str, str] = {
    "Node Operational Credentials": "Operational Credentials",
    "Demand Response and Load Control": "Demand Response Load Control",
    "WakeOnLAN": "Wake on LAN",
    "OnOff": "On/Off",
    "ota_provider": "ota_software_update_provider",
    "ota_requestor": "ota_software_update_requestor",
    "Dishwasher Alarm": "Dish Washer Alarm",
    "Dishwasher Mode": "Dish Washer Mode",
}

FEATURE_NAME_OVERRIDES: Dict[str, str] = {
    "WeekDayAccessSchedules": "weekday_access_schedules",
    "Auto": "fan_auto",
}

DEVICE_NAME_OVERRIDES: Dict[str, str] = {
    "Dishwasher": "Dish Washer",
}

ELEMENT_NAME_OVERRIDES: Dict[str, str] = {
    "RequirePINforRemoteOperation": "require_pin_for_remote_operation",
    "NextChargeTargetSoC": "next_charge_target_soc",
}

SKIP_INTERNALLY_MANAGED_ATTRIBUTE_FLAG: Dict[str, List[str]] = {
    "icd_management": [
        "user_active_mode_trigger_hint",
        "user_active_mode_trigger_instruction",
    ],
    "scenes_management": ["scene_table_size"],
    "thermostat": ["local_temperature", "remote_sensing"],
    "air_quality": ["air_quality"],
}

CLUSTER_CALLBACK_NAME_OVERRIDES: Dict[str, str] = {
    "ESPMatterWebrtcTransportProviderClusterServerInitCallback": "ESPMatterWebRTCTransportProviderClusterServerInitCallback",
    "ESPMatterWebrtcTransportProviderClusterServerShutdownCallback": "ESPMatterWebRTCTransportProviderClusterServerShutdownCallback",
    "ESPMatterWebrtcTransportRequestorClusterServerInitCallback": "ESPMatterWebRTCTransportRequestorClusterServerInitCallback",
    "ESPMatterWebrtcTransportRequestorClusterServerShutdownCallback": "ESPMatterWebRTCTransportRequestorClusterServerShutdownCallback",
}

_CPP_RESERVED_WORDS: FrozenSet[str] = frozenset(
    word.lower()
    for word in [
        "auto",
        "switch",
        "case",
        "default",
        "enum",
        "struct",
        "union",
        "typedef",
        "using",
        "static",
        "const",
        "volatile",
        "inline",
        "extern",
        "register",
        "restrict",
        "typeof",
        "void",
        "char",
        "short",
        "int",
        "long",
        "float",
        "double",
        "signed",
        "unsigned",
        "bool",
        "true",
        "false",
        "nullptr",
        "new",
        "delete",
        "try",
        "catch",
        "throw",
        "public",
        "private",
        "protected",
        "virtual",
        "override",
        "final",
        "explicit",
        "namespace",
        "static_cast",
        "dynamic_cast",
        "reinterpret_cast",
        "const_cast",
        "static_assert",
        "thread_local",
        "constexpr",
        "constinit",
        "co_await",
        "co_return",
        "co_yield",
    ]
)

SPECIAL_CONFIG_LIST = {
    # Cluster name
    "icd_management": "CHIP_CONFIG_ENABLE_ICD_SERVER",
    # attribute name
    "endpoint_unique_id": "CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID",
    "commissioning_arl": "CHIP_CONFIG_USE_ACCESS_RESTRICTIONS",
    "arl": "CHIP_CONFIG_USE_ACCESS_RESTRICTIONS",
    # command name
    "review_fabric_restrictions": "CHIP_CONFIG_USE_ACCESS_RESTRICTIONS",
    # feature name
    "wifi_network_interface": "CHIP_DEVICE_CONFIG_ENABLE_WIFI",
    "thread_network_interface": "CHIP_DEVICE_CONFIG_ENABLE_THREAD",
    "ethernet_network_interface": "CHIP_DEVICE_CONFIG_ENABLE_ETHERNET",
    "long_idle_time_support": "CHIP_CONFIG_ENABLE_ICD_LIT",
    "check_in_protocol_support": "CHIP_CONFIG_ENABLE_ICD_CIP",
    "user_active_mode_trigger": "CHIP_CONFIG_ENABLE_ICD_UAT",
    # event name
}


def normalize_cluster_display_name(cluster_name: str) -> str:
    return CLUSTER_NAME_OVERRIDES.get(cluster_name, cluster_name)


def normalize_feature_name(feature_name: str) -> str:
    return FEATURE_NAME_OVERRIDES.get(feature_name, feature_name)


def normalize_device_type_name(device_type_name: str) -> str:
    return DEVICE_NAME_OVERRIDES.get(device_type_name, device_type_name)


def normalize_element_name(element_name: str) -> str:
    return ELEMENT_NAME_OVERRIDES.get(element_name, element_name)


def is_cpp_reserved_word(cpp_name: str) -> bool:
    return cpp_name.lower() in _CPP_RESERVED_WORDS


def should_skip_cluster_command_callbacks(cluster_name: str) -> bool:
    return cluster_name in COMMAND_CALLBACK_SKIP


def should_skip_command_callback(command_name: str) -> bool:
    return command_name in CALLBACK_STUB_SKIP


def should_skip_delegate_callback(cluster_name: str) -> bool:
    return cluster_name in DELEGATE_CALLBACK_SKIP


def should_include_delegate_callback(cluster_name: str) -> bool:
    return cluster_name in DELEGATE_CALLBACK_INCLUDE


def should_skip_plugin_callback(cluster_name: str) -> bool:
    return cluster_name in PLUGIN_CALLBACK_SKIP


def should_skip_internally_managed_flag(cluster_name: str, attribute_name: str) -> bool:
    return (
        cluster_name in SKIP_INTERNALLY_MANAGED_ATTRIBUTE_FLAG
        and attribute_name in SKIP_INTERNALLY_MANAGED_ATTRIBUTE_FLAG[cluster_name]
    )


def get_overridden_cluster_init_callback_name(cluster_name: str) -> str:
    return CLUSTER_CALLBACK_NAME_OVERRIDES.get(
        f"ESPMatter{cluster_name}ClusterServerInitCallback",
        f"ESPMatter{cluster_name}ClusterServerInitCallback",
    )


def get_overridden_cluster_shutdown_callback_name(cluster_name: str) -> str:
    return CLUSTER_CALLBACK_NAME_OVERRIDES.get(
        f"ESPMatter{cluster_name}ClusterServerShutdownCallback",
        f"ESPMatter{cluster_name}ClusterServerShutdownCallback",
    )


def get_special_config_for_element(element_name: str) -> str:
    return SPECIAL_CONFIG_LIST.get(element_name, None)
