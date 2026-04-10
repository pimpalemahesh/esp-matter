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


def convert_to_int(value, default=None):
    """Convert a string or int value to an integer. Handles hex (0x...) and decimal strings."""
    if value is None:
        return default
    try:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value, 16) if value.startswith("0x") else int(value)
        return default
    except ValueError:
        return default


def hex_to_int(value):
    """Convert a hex string (or list of hex strings) to integer(s)."""
    if isinstance(value, list):
        return [hex_to_int(v) for v in value]
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 16)
    return value


def is_hex_value(value):
    """Check if a value is a valid hex value e.g. 0x0001"""
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def format_hex_value(hex_value):
    """Format a hex value by removing unnecessary leading zeros e.g. 0x00000001 -> 0x0001"""
    if hex_value and hex_value.startswith("0x"):
        int_value = int(hex_value, 16)
        return f"0x{int_value:04X}"
    return hex_value
