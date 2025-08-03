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

/* This is a Generated File */

#pragma once
#include <esp_matter_data_model.h>

#include <descriptor.h>
#include <binding.h>
#include <identify.h>
#include <groups.h>
#include <on_off.h>
#include <level_control.h>
#include <scenes_management.h>
#include <pump_configuration_and_control.h>
#include <temperature_measurement.h>
#include <pressure_measurement.h>
#include <flow_measurement.h>

#include <esp_matter.h>
#include <esp_matter_core.h>

using namespace esp_matter;

namespace esp_matter {
namespace endpoint {
namespace pump_controller {

constexpr uint32_t ESP_MATTER_PUMP_CONTROLLER_DEVICE_TYPE_ID = 0x0304;
constexpr uint8_t ESP_MATTER_PUMP_CONTROLLER_DEVICE_TYPE_VERSION = 4;

typedef struct config {
    cluster::descriptor::config_t descriptor;
    cluster::binding::config_t binding;
    cluster::identify::config_t identify;
    cluster::on_off::config_t on_off;
    cluster::pump_configuration_and_control::config_t pump_configuration_and_control;
} config_t;

uint32_t get_device_type_id();
uint8_t get_device_type_version();
endpoint_t *create(node_t *node, config_t *config, uint8_t flags, void *priv_data);
esp_err_t add(endpoint_t *endpoint, config_t *config);
} /* pump_controller */
} /* endpoint */
} /* esp_matter */