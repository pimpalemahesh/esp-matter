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

"""Tests for utils/conversion_utils.py — hex/int conversions and validation."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conversion_utils import convert_to_int, format_hex_value, hex_to_int, is_hex_value


class TestConvertToInt(unittest.TestCase):
    """Test convert_to_int() — flexible integer conversion."""

    def test_hex_string(self):
        self.assertEqual(convert_to_int("0x0A"), 10)

    def test_decimal_string(self):
        self.assertEqual(convert_to_int("200"), 200)

    def test_int_passthrough(self):
        self.assertEqual(convert_to_int(42), 42)

    def test_none_returns_default(self):
        self.assertEqual(convert_to_int(None, default=0), 0)

    def test_none_returns_none(self):
        self.assertIsNone(convert_to_int(None))

    def test_invalid_string_returns_default(self):
        self.assertEqual(convert_to_int("abc", default=0), 0)

    def test_float_returns_default(self):
        self.assertIsNone(convert_to_int(3.14))

    def test_zero(self):
        self.assertEqual(convert_to_int("0"), 0)

    def test_negative(self):
        self.assertEqual(convert_to_int("-5"), -5)


class TestHexToInt(unittest.TestCase):
    """Test hex_to_int() — hex string to integer conversion."""

    def test_hex_string(self):
        self.assertEqual(hex_to_int("0x0A"), 10)

    def test_int_passthrough(self):
        self.assertEqual(hex_to_int(42), 42)

    def test_list_conversion(self):
        result = hex_to_int(["0x01", "0x0A"])
        self.assertEqual(result, [1, 10])

    def test_non_hex_string(self):
        self.assertEqual(hex_to_int("FF"), 255)

    def test_other_type(self):
        self.assertIsNone(hex_to_int(None))


class TestIsHexValue(unittest.TestCase):
    """Test is_hex_value() — hex string validation."""

    def test_valid_hex_with_prefix(self):
        self.assertTrue(is_hex_value("0x0001"))

    def test_valid_hex_without_prefix(self):
        self.assertTrue(is_hex_value("FF"))

    def test_invalid_hex(self):
        self.assertFalse(is_hex_value("0xGGGG"))

    def test_decimal_as_hex(self):
        self.assertTrue(is_hex_value("123"))


class TestFormatHexValue(unittest.TestCase):
    """Test format_hex_value() — normalize hex formatting."""

    def test_long_hex(self):
        self.assertEqual(format_hex_value("0x00000001"), "0x0001")

    def test_short_hex(self):
        self.assertEqual(format_hex_value("0x01"), "0x0001")

    def test_already_formatted(self):
        self.assertEqual(format_hex_value("0x0001"), "0x0001")

    def test_large_value(self):
        self.assertEqual(format_hex_value("0xFFFF"), "0xFFFF")

    def test_non_hex(self):
        self.assertEqual(format_hex_value("hello"), "hello")

    def test_none(self):
        self.assertIsNone(format_hex_value(None))


if __name__ == "__main__":
    unittest.main()
