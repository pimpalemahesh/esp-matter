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
import yaml

from utils.helper import esp_name


class YamlParser:
    """Parser for YAML configuration files"""

    def __init__(self, file_path: str):
        """Initialize the YAML parser

        Args:
            file_path: Path to the YAML file
        """
        self.file_path = file_path
        with open(file_path, "r") as file:
            self.config = yaml.safe_load(file)

    def is_present(self, key: str) -> bool:
        """Check if a key exists in the YAML configuration

        Args:
            key: The key to check
        Returns:
            True if the key exists, False otherwise
        """
        return key in self.config

    def get_list(self, key: str) -> list:
        """Get a list of values from the YAML configuration

        Args:
            key: The key to get values for
        Returns:
            A list of values from the YAML configuration
        """
        return self.config.get(key, [])

    def is_present_in_list(self, key: str, value: str) -> bool:
        """Check if a value exists in a list in the YAML configuration

        Args:
            key: The key to check in the YAML configuration
            value: The value to check for
        Returns:
            True if the value exists in the list, False otherwise
        """
        if self.is_present(key):
            return any(esp_name(value) == esp_name(item) for item in self.get_list(key))
        return False
