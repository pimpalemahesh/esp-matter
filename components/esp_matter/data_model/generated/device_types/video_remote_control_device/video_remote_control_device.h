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
#include <binding.h>
#include <on_off.h>
#include <level_control.h>
#include <wake_on_lan.h>
#include <channel.h>
#include <target_navigator.h>
#include <media_playback.h>
#include <media_input.h>
#include <low_power.h>
#include <keypad_input.h>
#include <content_launcher.h>
#include <audio_output.h>
#include <application_launcher.h>
#include <account_login.h>
#include <content_control.h>

#include <esp_matter.h>
#include <esp_matter_core.h>

#define ESP_MATTER_VIDEO_REMOTE_CONTROL_DEVICE_TYPE_ID 0x002A
#define ESP_MATTER_VIDEO_REMOTE_CONTROL_DEVICE_TYPE_VERSION 2

namespace esp_matter {
namespace endpoint {
namespace video_remote_control {

typedef struct config {
    cluster::descriptor::config_t descriptor;
    cluster::binding::config_t binding;
} config_t;

uint32_t get_device_type_id();
uint8_t get_device_type_version();
endpoint_t *create(node_t *node, config_t *config, uint8_t flags, void *priv_data);
esp_err_t add(endpoint_t *endpoint, config_t *config);
} /* video_remote_control */
} /* endpoint */
} /* esp_matter */