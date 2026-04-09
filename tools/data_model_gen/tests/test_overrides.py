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

"""Tests for utils/overrides.py — name overrides, reserved words, skip lists, special config."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.overrides import (
    normalize_cluster_display_name,
    normalize_feature_name,
    normalize_device_type_name,
    normalize_element_name,
    is_cpp_reserved_word,
    should_skip_cluster_command_callbacks,
    should_skip_delegate_callback,
    should_include_delegate_callback,
    should_skip_plugin_callback,
    should_skip_internally_managed_flag,
    get_overridden_cluster_init_callback_name,
    get_overridden_cluster_shutdown_callback_name,
    get_special_config_for_element,
)


class TestClusterNameOverrides(unittest.TestCase):
    """Test cluster display name normalization."""

    def test_onoff_override(self):
        self.assertEqual(normalize_cluster_display_name("OnOff"), "On/Off")

    def test_operational_credentials_override(self):
        self.assertEqual(
            normalize_cluster_display_name("Node Operational Credentials"),
            "Operational Credentials",
        )

    def test_dishwasher_override(self):
        self.assertEqual(
            normalize_cluster_display_name("Dishwasher Mode"),
            "Dish Washer Mode",
        )

    def test_no_override(self):
        self.assertEqual(normalize_cluster_display_name("Thermostat"), "Thermostat")


class TestFeatureNameOverrides(unittest.TestCase):
    """Test feature name normalization."""

    def test_auto_override(self):
        self.assertEqual(normalize_feature_name("Auto"), "fan_auto")

    def test_weekday_override(self):
        self.assertEqual(
            normalize_feature_name("WeekDayAccessSchedules"),
            "weekday_access_schedules",
        )

    def test_no_override(self):
        self.assertEqual(normalize_feature_name("Lighting"), "Lighting")


class TestDeviceNameOverrides(unittest.TestCase):
    """Test device type name normalization."""

    def test_dishwasher_override(self):
        self.assertEqual(normalize_device_type_name("Dishwasher"), "Dish Washer")

    def test_no_override(self):
        self.assertEqual(normalize_device_type_name("Fan"), "Fan")


class TestElementNameOverrides(unittest.TestCase):
    """Test element name normalization."""

    def test_pin_override(self):
        self.assertEqual(
            normalize_element_name("RequirePINforRemoteOperation"),
            "require_pin_for_remote_operation",
        )

    def test_soc_override(self):
        self.assertEqual(
            normalize_element_name("NextChargeTargetSoC"),
            "next_charge_target_soc",
        )

    def test_no_override(self):
        self.assertEqual(normalize_element_name("temperature"), "temperature")


class TestCppReservedWords(unittest.TestCase):
    """Test C++ reserved word detection."""

    def test_switch_is_reserved(self):
        self.assertTrue(is_cpp_reserved_word("switch"))

    def test_auto_is_reserved(self):
        self.assertTrue(is_cpp_reserved_word("auto"))

    def test_case_insensitive(self):
        self.assertTrue(is_cpp_reserved_word("SWITCH"))
        self.assertTrue(is_cpp_reserved_word("Switch"))

    def test_non_reserved(self):
        self.assertFalse(is_cpp_reserved_word("temperature"))
        self.assertFalse(is_cpp_reserved_word("on_off"))

    def test_common_keywords(self):
        for word in ["const", "void", "int", "bool", "true", "false", "namespace"]:
            self.assertTrue(is_cpp_reserved_word(word), f"{word} should be reserved")


class TestSkipLists(unittest.TestCase):
    """Test skip/include callback logic."""

    def test_skip_command_callback(self):
        self.assertTrue(should_skip_cluster_command_callbacks("bridged_device_basic_information"))

    def test_no_skip_command_callback(self):
        self.assertFalse(should_skip_cluster_command_callbacks("on_off"))

    def test_skip_delegate_callback(self):
        self.assertTrue(should_skip_delegate_callback("webrtc_transport_provider"))

    def test_no_skip_delegate_callback(self):
        self.assertFalse(should_skip_delegate_callback("thermostat"))

    def test_include_delegate_callback(self):
        self.assertTrue(should_include_delegate_callback("mode_select"))

    def test_no_include_delegate_callback(self):
        self.assertFalse(should_include_delegate_callback("thermostat"))

    def test_skip_plugin_callback(self):
        self.assertTrue(should_skip_plugin_callback("icd_management"))

    def test_no_skip_plugin_callback(self):
        self.assertFalse(should_skip_plugin_callback("on_off"))


class TestInternallyManagedSkip(unittest.TestCase):
    """Test internally managed attribute skip logic."""

    def test_skip_icd_attribute(self):
        self.assertTrue(
            should_skip_internally_managed_flag("icd_management", "user_active_mode_trigger_hint")
        )

    def test_skip_thermostat_attribute(self):
        self.assertTrue(
            should_skip_internally_managed_flag("thermostat", "local_temperature")
        )

    def test_no_skip_unknown_cluster(self):
        self.assertFalse(
            should_skip_internally_managed_flag("on_off", "on_off")
        )

    def test_no_skip_unknown_attribute(self):
        self.assertFalse(
            should_skip_internally_managed_flag("thermostat", "system_mode")
        )


class TestCallbackNameOverrides(unittest.TestCase):
    """Test WebRTC callback name overrides."""

    def test_webrtc_provider_init(self):
        result = get_overridden_cluster_init_callback_name("WebrtcTransportProvider")
        self.assertIn("WebRTC", result)

    def test_webrtc_requestor_shutdown(self):
        result = get_overridden_cluster_shutdown_callback_name("WebrtcTransportRequestor")
        self.assertIn("WebRTC", result)

    def test_no_override(self):
        result = get_overridden_cluster_init_callback_name("Thermostat")
        self.assertEqual(result, "ESPMatterThermostatClusterServerInitCallback")


class TestSpecialConfig(unittest.TestCase):
    """Test special config (preprocessor guard) lookups."""

    def test_icd_management(self):
        self.assertEqual(get_special_config_for_element("icd_management"), "CHIP_CONFIG_ENABLE_ICD_SERVER")

    def test_wifi_feature(self):
        self.assertEqual(get_special_config_for_element("wifi_network_interface"), "CHIP_DEVICE_CONFIG_ENABLE_WIFI")

    def test_thread_feature(self):
        self.assertEqual(get_special_config_for_element("thread_network_interface"), "CHIP_DEVICE_CONFIG_ENABLE_THREAD")

    def test_no_special_config(self):
        self.assertIsNone(get_special_config_for_element("on_off"))


if __name__ == "__main__":
    unittest.main()
