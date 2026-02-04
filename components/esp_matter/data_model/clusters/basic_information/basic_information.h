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

#pragma once
#include <esp_matter_data_model.h>

namespace esp_matter {
namespace cluster {
namespace basic_information {

namespace attribute {
attribute_t *create_data_model_revision(cluster_t *cluster, uint16_t value);
attribute_t *create_vendor_name(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_vendor_id(cluster_t *cluster, uint16_t value);
attribute_t *create_product_name(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_product_id(cluster_t *cluster, uint16_t value);
attribute_t *create_node_label(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_location(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_hardware_version(cluster_t *cluster, uint16_t value);
attribute_t *create_hardware_version_string(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_software_version(cluster_t *cluster, uint32_t value);
attribute_t *create_software_version_string(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_manufacturing_date(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_part_number(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_product_url(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_product_label(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_serial_number(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_local_config_disabled(cluster_t *cluster, bool value);
attribute_t *create_reachable(cluster_t *cluster, bool value);
attribute_t *create_unique_id(cluster_t *cluster, char * value, uint16_t length);
attribute_t *create_capability_minima(cluster_t *cluster, uint8_t * value, uint16_t length, uint16_t count);
attribute_t *create_product_appearance(cluster_t *cluster, uint8_t * value, uint16_t length, uint16_t count);
attribute_t *create_specification_version(cluster_t *cluster, uint32_t value);
attribute_t *create_max_paths_per_invoke(cluster_t *cluster, uint16_t value);
} /* attribute */

namespace event {
event_t *create_start_up(cluster_t *cluster);
event_t *create_shut_down(cluster_t *cluster);
event_t *create_leave(cluster_t *cluster);
event_t *create_reachable_changed(cluster_t *cluster);
} /* event */

typedef struct config {
    config() {}
} config_t;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags);

} /* basic_information */
} /* cluster */
} /* esp_matter */