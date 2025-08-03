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

/* This is a Generated File */

#pragma once
#include <esp_matter_data_model.h>

#include <descriptor.h>
#include <identify.h>
#include <air_quality.h>
#include <temperature_measurement.h>
#include <relative_humidity_measurement.h>
#include <carbon_monoxide_concentration_measurement.h>
#include <carbon_dioxide_concentration_measurement.h>
#include <nitrogen_dioxide_concentration_measurement.h>
#include <ozone_concentration_measurement.h>
#include <pm2_5_concentration_measurement.h>
#include <formaldehyde_concentration_measurement.h>
#include <pm1_concentration_measurement.h>
#include <pm10_concentration_measurement.h>
#include <total_volatile_organic_compounds_concentration_measurement.h>
#include <radon_concentration_measurement.h>

#include <esp_matter.h>
#include <esp_matter_core.h>

#define ESP_MATTER_AIR_QUALITY_SENSOR_DEVICE_TYPE_ID 0x002C
#define ESP_MATTER_AIR_QUALITY_SENSOR_DEVICE_TYPE_VERSION 1

using namespace esp_matter;

namespace esp_matter {
namespace endpoint {
namespace air_quality_sensor {

typedef struct config {
    cluster::descriptor::config_t descriptor;
    cluster::identify::config_t identify;
    cluster::air_quality::config_t air_quality;
} config_t;

uint32_t get_device_type_id();
uint8_t get_device_type_version();
endpoint_t *create(node_t *node, config_t *config, uint8_t flags, void *priv_data);
esp_err_t add(endpoint_t *endpoint, config_t *config);
} /* air_quality_sensor */
} /* endpoint */
} /* esp_matter */