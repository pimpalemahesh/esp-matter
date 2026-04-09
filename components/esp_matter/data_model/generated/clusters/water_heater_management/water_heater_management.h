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

#pragma once
#include <esp_matter_data_model.h>

namespace esp_matter {
namespace cluster {
namespace water_heater_management {

namespace feature {
namespace energy_management {
uint32_t get_id();
esp_err_t add(cluster_t *cluster);
} /* energy_management */

namespace tank_percent {
uint32_t get_id();
esp_err_t add(cluster_t *cluster);
} /* tank_percent */

} /* feature */

namespace attribute {
attribute_t *create_heater_types(cluster_t *cluster, uint8_t value);
attribute_t *create_heat_demand(cluster_t *cluster, uint8_t value);
attribute_t *create_tank_volume(cluster_t *cluster, uint16_t value);
attribute_t *create_estimated_heat_required(cluster_t *cluster, int64_t value);
attribute_t *create_tank_percentage(cluster_t *cluster, uint8_t value);
attribute_t *create_boost_state(cluster_t *cluster, uint8_t value);
} /* attribute */

namespace command {
command_t *create_boost(cluster_t *cluster);
command_t *create_cancel_boost(cluster_t *cluster);
} /* command */

namespace event {
event_t *create_boost_started(cluster_t *cluster);
event_t *create_boost_ended(cluster_t *cluster);
} /* event */

typedef struct config {
    void *delegate;
    config() : delegate(nullptr) {}
} config_t;

cluster_t *create(endpoint_t *endpoint, config_t *config, uint8_t flags);

} /* water_heater_management */
} /* cluster */
} /* esp_matter */
