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

"""Tests for custom exception classes (XmlParseError, CodeGenerationError, ConfigurationError)."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.exceptions import (
    DataModelGenError,
    XmlParseError,
    CodeGenerationError,
    ConfigurationError,
)


class TestDataModelGenError(unittest.TestCase):
    """Tests for base DataModelGenError."""

    def test_message_only(self):
        e = DataModelGenError("Something failed")
        self.assertEqual(str(e), "Something failed")
        self.assertIn("Something failed", e.args[0])

    def test_with_context(self):
        e = DataModelGenError(
            "Invalid element",
            file_path="/path/to/file.xml",
            line_number=10,
            context="cluster Foo",
            suggestion="Check the XML schema.",
        )
        msg = e.args[0]
        self.assertIn("Invalid element", msg)
        self.assertIn("File: /path/to/file.xml", msg)
        self.assertIn("Line: 10", msg)
        self.assertIn("cluster Foo", msg)
        self.assertIn("Check the XML schema", msg)
        self.assertEqual(e.file_path, "/path/to/file.xml")
        self.assertEqual(e.line_number, 10)


class TestXmlParseError(unittest.TestCase):
    """Tests for XmlParseError (xml_processing)."""

    def test_inherits_from_data_model_gen_error(self):
        self.assertTrue(issubclass(XmlParseError, DataModelGenError))

    def test_raise_and_catch(self):
        with self.assertRaises(DataModelGenError) as ctx:
            raise XmlParseError(
                "Attribute type is None",
                context="resolve_attribute_type",
                suggestion="Add a type attribute.",
            )
        self.assertIsInstance(ctx.exception, XmlParseError)
        self.assertIn("Attribute type is None", str(ctx.exception))

    def test_used_in_xml_processing(self):
        from xml_processing.data_type_parser import resolve_attribute_type
        from xml.etree.ElementTree import Element

        elem = Element("attribute")
        elem.set("name", "test")
        with self.assertRaises(XmlParseError) as ctx:
            resolve_attribute_type(elem, {})
        self.assertIn("type", str(ctx.exception).lower())


class TestCodeGenerationError(unittest.TestCase):
    """Tests for CodeGenerationError (code_generation)."""

    def test_inherits_from_data_model_gen_error(self):
        self.assertTrue(issubclass(CodeGenerationError, DataModelGenError))

    def test_raise_and_catch(self):
        with self.assertRaises(DataModelGenError) as ctx:
            raise CodeGenerationError(
                "Template render failed",
                file_path="cluster.h.jinja",
                suggestion="Check template syntax.",
            )
        self.assertIsInstance(ctx.exception, CodeGenerationError)
        self.assertIn("Template render failed", str(ctx.exception))

    def test_used_in_conformance_codegen(self):
        from code_generation.conformance_codegen import parse_expr
        from utils.conformance import ConformanceTAG

        obj = {ConformanceTAG.COMMAND.value: "foo"}
        with self.assertRaises(CodeGenerationError) as ctx:
            parse_expr(obj)
        self.assertIn("Command flag", str(ctx.exception))


class TestConfigurationError(unittest.TestCase):
    """Tests for ConfigurationError (configuration)."""

    def test_inherits_from_data_model_gen_error(self):
        self.assertTrue(issubclass(ConfigurationError, DataModelGenError))

    def test_raise_and_catch(self):
        with self.assertRaises(DataModelGenError) as ctx:
            raise ConfigurationError(
                "ESP_MATTER_PATH is not set",
                context="main",
                suggestion="Set the environment variable.",
            )
        self.assertIsInstance(ctx.exception, ConfigurationError)
        self.assertIn("ESP_MATTER_PATH", str(ctx.exception))

    def test_set_esp_matter_path_empty_raises(self):
        import utils.config as config

        with self.assertRaises(ConfigurationError) as ctx:
            config.set_esp_matter_path("")
        self.assertIn("empty", str(ctx.exception).lower())
        with self.assertRaises(ConfigurationError):
            config.set_esp_matter_path("   ")

    def test_set_esp_matter_path_nonexistent_dir_raises(self):
        import utils.config as config

        with self.assertRaises(ConfigurationError) as ctx:
            config.set_esp_matter_path("/nonexistent/path/12345")
        self.assertIn("directory", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
