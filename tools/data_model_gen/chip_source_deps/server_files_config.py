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

from tree_sitter import Parser
from tree_sitter_languages import get_language

LANG_CPP = get_language("cpp")
parser = Parser()
parser.set_language(LANG_CPP)

# Plugin init callback pattern
PLUGIN_CB_PATTERN = r"\bvoid\s+Matter(\w+)PluginServerInitCallback\s*\("

# Delegate related methods
DELEGATE_METHODS = ["GetDelegate", "SetDefaultDelegate", "SetDelegate"]

# Member variable
DELEGATE_VARIABLE_NAMES = ["mDelegate"]

# Regex to capture case statements like case <attribute_name>:Id:
ATTRIBUTE_REGEX = r"case\s+([\w:]+)(?:::Id)?:"

# Search for these function names in server files for internally managed attributes
KEYWORDS = ["Read(", "ReadAttribute(", "ReadImpl("]

ATTRIBUTE_PATTERN = (
    r"namespace\s+(\w+)\s*{[\s\n]*inline\s+constexpr\s+AttributeId\s+Id\s*=\s*([\w:]+);"
)
COMMAND_PATTERN = (
    r"namespace\s+(\w+)\s*{[\s\n]*inline\s+constexpr\s+CommandId\s+Id\s*=\s*([\w:]+);"
)
EVENT_PATTERN = (
    r"namespace\s+(\w+)\s*{[\s\n]*inline\s+constexpr\s+EventId\s+Id\s*=\s*([\w:]+);"
)
CLUSTER_ID_PATTERN = r"inline\s+constexpr\s+ClusterId\s+Id\s*=\s*([\w:]+);"

local_mappings = {
    "dishwasher": "dish_washer",
    "dishwasher_alarm": "dish_washer_alarm",
    "dishwasher_mode": "dish_washer_mode",
    "ota_requestor": "ota_software_update_requestor",
    "ota_provider": "ota_software_update_provider",
    "group_key_mgmt": "group_key_management",
    "bindings": "binding",
    "boolean_state": "boolean_state_configuration",
}
