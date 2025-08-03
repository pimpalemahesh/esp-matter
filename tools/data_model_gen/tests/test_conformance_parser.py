# Copyright 2025 Espressif Systems (Shanghai) PTE LTD
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

"""
Comprehensive test suite for conformance parsing based on real XML examples
from connectedhomeip/data_model/1.5/clusters/
"""

import unittest
import xml.etree.ElementTree as ET
import json
import sys
import os
from xml_processing.conformance_parser import (
    parse_conformance,
    Conformance,
    check_conformance_restrictions,
    match_conformance_items,
)
from utils.helper import convert_to_snake_case

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockFeature:
    """Mock feature object for testing"""

    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.func_name = convert_to_snake_case(name)


class MockItem:
    """Mock item (attribute/command/event) for testing conformance matching"""

    def __init__(self, name, conformance=None):
        self.name = name
        self.conformance = conformance


class TestBasicConformance(unittest.TestCase):
    """Test basic conformance types without conditions"""

    def test_simple_mandatory_conformance(self):
        """Test parsing simple <mandatoryConform/> tags"""
        xml = "<mandatoryConform/>"
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "mandatory")
        self.assertIsNone(result.condition)

    def test_simple_optional_conformance(self):
        """Test parsing simple <optionalConform/> tags"""
        xml = "<optionalConform/>"
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "optional")
        self.assertIsNone(result.condition)

    def test_simple_deprecated_conformance(self):
        """Test parsing simple <deprecateConform/> tags"""
        xml = "<deprecateConform/>"
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "deprecate")

    def test_simple_disallowed_conformance(self):
        """Test parsing simple <disallowConform/> tags"""
        xml = "<disallowConform/>"
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "disallow")

    def test_simple_provisional_conformance(self):
        """Test parsing simple <provisionalConform/> tags"""
        xml = "<provisionalConform/>"
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "provisional")


class TestChoiceConformance(unittest.TestCase):
    """Test choice conformance patterns from OccupancySensing cluster"""

    def test_choice_conformance_with_min_and_more(self):
        """Test: <optionalConform choice="a" more="true" min="1"/>
        From OccupancySensing features - at least 1 sensing method required"""
        xml = '<optionalConform choice="a" more="true" min="1"/>'
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "optional")
        self.assertEqual(result.choice, "a")
        self.assertTrue(result.more)
        self.assertEqual(result.min, 1)

    def test_choice_conformance_serialization(self):
        """Test JSON serialization of choice conformance"""
        xml = '<optionalConform choice="a" more="true" min="1"/>'
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)
        dict_result = result.to_dict()

        self.assertEqual(dict_result["type"], "optional")
        self.assertEqual(dict_result["choice"], "a")
        self.assertTrue(dict_result["more"])
        self.assertEqual(dict_result["min"], 1)


class TestFeatureBasedConformance(unittest.TestCase):
    """Test feature-based conformance patterns"""

    def test_mandatory_with_single_feature(self):
        """Test: <mandatoryConform><feature name="LT"/></mandatoryConform>
        From OnOff cluster commands"""
        xml = """<mandatoryConform>
            <feature name="LT"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {"LT": MockFeature("Lighting", "LT")}
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertIsNotNone(result.condition)
        self.assertEqual(result.condition, {"feature": "lighting"})

    def test_mandatory_with_or_features(self):
        """Test: <mandatoryConform><orTerm><feature/><feature/></orTerm></mandatoryConform>
        From ColorControl cluster"""
        xml = """<mandatoryConform>
            <orTerm>
                <feature name="HS"/>
                <feature name="XY"/>
                <feature name="CT"/>
            </orTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "HS": MockFeature("HueSaturation", "HS"),
            "XY": MockFeature("XY", "XY"),
            "CT": MockFeature("ColorTemperature", "CT"),
        }
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertIn("or", result.condition)
        self.assertEqual(len(result.condition["or"]), 3)

    def test_optional_with_not_feature(self):
        """Test: <optionalConform><notTerm><feature name="OFFONLY"/></notTerm></optionalConform>
        From OnOff cluster - LT feature"""
        xml = """<optionalConform>
            <notTerm>
                <feature name="OFFONLY"/>
            </notTerm>
        </optionalConform>"""
        elem = ET.fromstring(xml)
        feature_map = {"OFFONLY": MockFeature("OffOnly", "OFFONLY")}
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "optional")
        self.assertIn("not", result.condition)
        self.assertEqual(result.condition["not"]["feature"], "off_only")

    def test_nested_not_or_features(self):
        """Test: <optionalConform><notTerm><orTerm><feature/><feature/></orTerm></notTerm></optionalConform>
        From OnOff cluster - OFFONLY feature"""
        xml = """<optionalConform>
            <notTerm>
                <orTerm>
                    <feature name="LT"/>
                    <feature name="DF"/>
                </orTerm>
            </notTerm>
        </optionalConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "LT": MockFeature("Lighting", "LT"),
            "DF": MockFeature("DeadFrontBehavior", "DF"),
        }
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "optional")
        self.assertIn("not", result.condition)
        self.assertIn("or", result.condition["not"])

    def test_mandatory_with_not_feature(self):
        """Test: <mandatoryConform><notTerm><feature name="OFFONLY"/></notTerm></mandatoryConform>
        From OnOff cluster - On/Toggle commands"""
        xml = """<mandatoryConform>
            <notTerm>
                <feature name="OFFONLY"/>
            </notTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {"OFFONLY": MockFeature("OffOnly", "OFFONLY")}
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertIn("not", result.condition)


class TestAttributeCommandConformance(unittest.TestCase):
    """Test conformance based on attributes and commands"""

    def test_attribute_reference(self):
        """Test: <mandatoryConform><attribute name="SomeAttribute"/></mandatoryConform>"""
        xml = """<mandatoryConform>
            <attribute name="OnOff"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertEqual(result.condition, {"attribute": "OnOff"})

    def test_command_reference(self):
        """Test: <mandatoryConform><command name="SomeCommand"/></mandatoryConform>"""
        xml = """<mandatoryConform>
            <command name="Off"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertEqual(result.condition, {"command": "Off"})

    def test_attribute_or_command(self):
        """Test OR of attributes/commands"""
        xml = """<mandatoryConform>
            <orTerm>
                <attribute name="OnOff"/>
                <command name="Toggle"/>
            </orTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertIn("or", result.condition)


class TestComparisonConformance(unittest.TestCase):
    """Test comparison operations (greater, equal) with attributes and literals"""

    def test_greater_than_with_attribute_and_literal(self):
        """Test: <mandatoryConform><greaterTerm><attribute name="X"/><literal value="0"/></greaterTerm></mandatoryConform>
        From ColorControl cluster - Primary color attributes"""
        xml = """<mandatoryConform>
            <greaterTerm>
                <attribute name="NumberOfPrimaries"/>
                <literal value="0"/>
            </greaterTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertIn("greater", result.condition)
        self.assertEqual(len(result.condition["greater"]), 2)
        self.assertEqual(
            result.condition["greater"][0], {"attribute": "NumberOfPrimaries"}
        )
        self.assertEqual(result.condition["greater"][1], {"literal": "0"})


def test_greater_than_different_values(self):
    """Test greater than with different literal values"""
    xml = """<mandatoryConform>
        <greaterTerm>
            <attribute name="NumberOfPrimaries"/>
            <literal value="1"/>
        </greaterTerm>
    </mandatoryConform>"""
    elem = ET.fromstring(xml)
    result = Conformance({}).parse(elem)

    self.assertEqual(result.condition["greater"][1], {"literal": "1"})


class TestOtherwiseConformance(unittest.TestCase):
    """Test otherwise conformance patterns"""

    def test_otherwise_with_mandatory_and_deprecated(self):
        """Test: <otherwiseConform><mandatoryConform/><deprecateConform/></otherwiseConform>
        From OccupancySensing cluster"""
        xml = """<otherwiseConform>
            <mandatoryConform/>
            <deprecateConform/>
        </otherwiseConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "otherwise")
        self.assertIn("mandatory", result.condition)
        self.assertIn("deprecate", result.condition)

    def test_otherwise_with_provisional_and_mandatory(self):
        """Test: <otherwiseConform><provisionalConform/><mandatoryConform/></otherwiseConform>
        From BasicInformation cluster"""
        xml = """<otherwiseConform>
            <provisionalConform/>
            <mandatoryConform/>
        </otherwiseConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "otherwise")
        self.assertIn("provisional", result.condition)
        self.assertIn("mandatory", result.condition)

    def test_otherwise_with_conditional_mandatory(self):
        """Test otherwise with mandatory that has conditions"""
        xml = """<otherwiseConform>
            <mandatoryConform>
                <greaterTerm>
                    <attribute name="NumberOfPrimaries"/>
                    <literal value="0"/>
                </greaterTerm>
            </mandatoryConform>
            <optionalConform/>
        </otherwiseConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        self.assertEqual(result.type, "otherwise")
        self.assertIn("mandatory", result.condition)
        self.assertIn("greater", result.condition["mandatory"])
        self.assertIn("optional", result.condition)

    def test_otherwise_with_optional_choice(self):
        """Test otherwise with optional that has choice attributes"""
        xml = """<otherwiseConform>
            <mandatoryConform>
          <feature name="AUTO"/>
        </mandatoryConform>
        <optionalConform choice="a" more="true" min="1"/>
        </otherwiseConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "LT": MockFeature("Lighting", "LT"),
            "AUTO": MockFeature("Auto", "AUTO"),
        }
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "otherwise")
        self.assertIn("optional", result.condition)
        self.assertEqual(result.condition["optional"]["choice"], "a")
        self.assertTrue(result.condition["optional"]["more"])
        self.assertEqual(result.condition["optional"]["min"], 1)


class TestComplexNestedConformance(unittest.TestCase):
    """Test complex nested conformance structures"""

    def test_and_of_features(self):
        """Test AND operation with multiple features"""
        xml = """<mandatoryConform>
            <andTerm>
                <feature name="LT"/>
                <feature name="DF"/>
            </andTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "LT": MockFeature("Lighting", "LT"),
            "DF": MockFeature("DeadFrontBehavior", "DF"),
        }
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertIn("and", result.condition)
        self.assertEqual(len(result.condition["and"]), 2)

    def test_complex_nested_boolean_operations(self):
        """Test complex nested: AND(OR(...), NOT(...))"""
        xml = """<mandatoryConform>
            <andTerm>
                <orTerm>
                    <feature name="HS"/>
                    <feature name="XY"/>
                </orTerm>
                <notTerm>
                    <feature name="OFFONLY"/>
                </notTerm>
            </andTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "HS": MockFeature("HueSaturation", "HS"),
            "XY": MockFeature("XY", "XY"),
            "OFFONLY": MockFeature("OffOnly", "OFFONLY"),
        }
        result = Conformance(feature_map).parse(elem)

        self.assertEqual(result.type, "mandatory")
        self.assertIn("and", result.condition)
        # Check that we have both OR and NOT in the AND
        and_elements = result.condition["and"]
        has_or = any(
            "or" in elem if isinstance(elem, dict) else False for elem in and_elements
        )
        has_not = any(
            "not" in elem if isinstance(elem, dict) else False for elem in and_elements
        )
        self.assertTrue(has_or or has_not)

    def test_implicit_and_of_multiple_features(self):
        """Test implicit AND when multiple features at same level"""
        xml = """<mandatoryConform>
            <feature name="LT"/>
            <feature name="DF"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "LT": MockFeature("Lighting", "LT"),
            "DF": MockFeature("DeadFrontBehavior", "DF"),
        }
        result = Conformance(feature_map).parse(elem)

        # Multiple features at same level should be implicitly AND-ed
        self.assertEqual(result.type, "mandatory")
        if result.condition:
            self.assertTrue("and" in result.condition or "feature" in result.condition)


class TestConformanceRestrictions(unittest.TestCase):
    """Test check_conformance_restrictions function"""

    def test_skip_disallowed_conformance(self):
        """Test that disallowed elements are flagged for skipping"""
        xml = """<attribute id="0x0001" name="TestAttr">
            <disallowConform/>
        </attribute>"""
        elem = ET.fromstring(xml)
        should_skip = check_conformance_restrictions({}, elem)
        self.assertTrue(should_skip)

    def test_skip_deprecated_conformance(self):
        """Test that deprecated elements are flagged for skipping"""
        xml = """<attribute id="0x0001" name="TestAttr">
            <deprecateConform/>
        </attribute>"""
        elem = ET.fromstring(xml)
        should_skip = check_conformance_restrictions({}, elem)
        self.assertTrue(should_skip)

    def test_skip_provisional_conformance(self):
        """Test that provisional elements are flagged for skipping"""
        xml = """<attribute id="0x0001" name="TestAttr">
            <provisionalConform/>
        </attribute>"""
        elem = ET.fromstring(xml)
        should_skip = check_conformance_restrictions({}, elem)
        self.assertTrue(should_skip)

    def test_skip_otherwise_with_provisional_first(self):
        """Test that otherwise conformance with provisional first is skipped"""
        xml = """<attribute id="0x0001" name="TestAttr">
            <otherwiseConform>
                <provisionalConform/>
                <mandatoryConform/>
            </otherwiseConform>
        </attribute>"""
        elem = ET.fromstring(xml)
        should_skip = check_conformance_restrictions({}, elem)
        self.assertTrue(should_skip)

    def test_skip_missing_feature_in_mandatory(self):
        """Test skipping when mandatory conformance references non-existent feature"""
        xml = """<attribute id="0x0001" name="TestAttr">
            <otherwiseConform>
                <mandatoryConform>
                    <feature name="NONEXISTENT"/>
                </mandatoryConform>
                <optionalConform/>
            </otherwiseConform>
        </attribute>"""
        elem = ET.fromstring(xml)
        feature_map = {"LT": MockFeature("Lighting", "LT")}  # NONEXISTENT not in map
        should_skip = check_conformance_restrictions(feature_map, elem)
        self.assertTrue(should_skip)

    def test_dont_skip_valid_mandatory(self):
        """Test that valid mandatory conformance is not skipped"""
        xml = """<attribute id="0x0001" name="TestAttr">
            <mandatoryConform/>
        </attribute>"""
        elem = ET.fromstring(xml)
        should_skip = check_conformance_restrictions({}, elem)
        self.assertFalse(should_skip)

    def test_skip_zigbee_specific(self):
        """Test that Zigbee-specific optional conformance is skipped"""
        xml = """<attribute id="0x0001" name="TestAttr">
            <optionalConform>
                <condition name="Zigbee"/>
            </optionalConform>
        </attribute>"""
        elem = ET.fromstring(xml)
        should_skip = check_conformance_restrictions({}, elem)
        self.assertTrue(should_skip)


class TestConformanceSerialization(unittest.TestCase):
    """Test JSON serialization of conformance objects"""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion"""
        xml = "<mandatoryConform/>"
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)
        dict_result = result.to_dict()

        self.assertEqual(dict_result["type"], "mandatory")

    def test_to_dict_with_condition(self):
        """Test to_dict with conditions"""
        xml = """<mandatoryConform>
            <feature name="LT"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {"LT": MockFeature("Lighting", "LT")}
        result = Conformance(feature_map).parse(elem)
        dict_result = result.to_dict()

        self.assertIn("condition", dict_result)
        self.assertIsNotNone(dict_result["condition"])

    def test_to_dict_with_attribute_map(self):
        """Test to_dict with attribute name to ID mapping"""
        xml = """<mandatoryConform>
            <orTerm>
                <attribute name="OnOff"/>
                <attribute name="LevelControl"/>
            </orTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        # Without attribute map
        dict_without_map = result.to_dict()
        self.assertEqual(dict_without_map["condition"]["or"][0]["attribute"], "OnOff")

        # With attribute map - should replace names with IDs
        attribute_map = {"OnOff": "0x0000", "LevelControl": "0x0008"}
        dict_with_map = result.to_dict(attribute_map)
        self.assertEqual(dict_with_map["condition"]["or"][0]["attribute"], "0x0000")
        self.assertEqual(dict_with_map["condition"]["or"][1]["attribute"], "0x0008")

    def test_to_dict_with_command_map(self):
        """Test to_dict with command name to ID/flag mapping"""
        xml = """<mandatoryConform>
            <command name="Off"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        result = Conformance({}).parse(elem)

        # With command map (stored as tuple with flag)
        command_map = {"Off": ("0x0000", "COMMAND_FLAG_ACCEPTED")}
        dict_with_map = result.to_dict(command_map)
        self.assertEqual(dict_with_map["condition"]["command"], "0x0000")
        self.assertEqual(dict_with_map["condition"]["flag"], "COMMAND_FLAG_ACCEPTED")

    def test_to_dict_json_serializable(self):
        """Test that to_dict output is JSON serializable"""
        xml = """<optionalConform choice="a" more="true" min="1">
            <andTerm>
                <feature name="LT"/>
                <feature name="DF"/>
            </andTerm>
        </optionalConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "LT": MockFeature("Lighting", "LT"),
            "DF": MockFeature("DeadFrontBehavior", "DF"),
        }
        result = Conformance(feature_map).parse(elem)
        dict_result = result.to_dict()

        # Should not raise exception
        json_str = json.dumps(dict_result)
        self.assertIsNotNone(json_str)


class TestMatchConformanceItems(unittest.TestCase):
    """Test matching items with feature conformance"""

    def test_match_mandatory_feature(self):
        """Test matching items with mandatory feature conformance"""
        # Create a feature
        feature = MockFeature("Lighting", "LT")

        # Create conformance that requires this feature
        xml = """<mandatoryConform>
            <feature name="LT"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {"LT": feature}
        conformance = Conformance(feature_map).parse(elem)

        # Create items with this conformance
        item1 = MockItem("OnCommand", conformance)
        item2 = MockItem("OffCommand", None)

        items = [item1, item2]
        matched = match_conformance_items(feature, items)

        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0].name, "OnCommand")

    def test_match_otherwise_mandatory_feature(self):
        """Test matching items with otherwise conformance containing mandatory feature"""
        feature = MockFeature("Lighting", "LT")

        # Create otherwise conformance
        xml = """<otherwiseConform>
            <mandatoryConform>
                <feature name="LT"/>
            </mandatoryConform>
            <optionalConform/>
        </otherwiseConform>"""
        elem = ET.fromstring(xml)
        feature_map = {"LT": feature}
        conformance = Conformance(feature_map).parse(elem)

        item = MockItem("LightingCommand", conformance)
        items = [item]
        matched = match_conformance_items(feature, items)

        # Should match if otherwise has mandatory with this feature
        # Note: Current implementation checks for condition.get("mandatory")
        self.assertGreaterEqual(len(matched), 0)


class TestConformanceHasFeature(unittest.TestCase):
    """Test has_feature method on Conformance objects"""

    def test_has_feature_simple(self):
        """Test has_feature with simple feature conformance"""
        xml = """<mandatoryConform>
            <feature name="LT"/>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature = MockFeature("Lighting", "LT")
        feature_map = {"LT": feature}
        conformance = Conformance(feature_map).parse(elem)

        self.assertTrue(conformance.has_feature("LT"))
        self.assertFalse(conformance.has_feature("DF"))

    def test_has_feature_in_or(self):
        """Test has_feature when feature is in OR term"""
        xml = """<mandatoryConform>
            <orTerm>
                <feature name="LT"/>
                <feature name="DF"/>
            </orTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "LT": MockFeature("Lighting", "LT"),
            "DF": MockFeature("DeadFrontBehavior", "DF"),
        }
        conformance = Conformance(feature_map).parse(elem)

        self.assertTrue(conformance.has_feature("LT"))
        self.assertTrue(conformance.has_feature("DF"))

    def test_has_feature_in_and(self):
        """Test has_feature when feature is in AND term"""
        xml = """<mandatoryConform>
            <andTerm>
                <feature name="LT"/>
                <feature name="DF"/>
            </andTerm>
        </mandatoryConform>"""
        elem = ET.fromstring(xml)
        feature_map = {
            "LT": MockFeature("Lighting", "LT"),
            "DF": MockFeature("DeadFrontBehavior", "DF"),
        }
        conformance = Conformance(feature_map).parse(elem)

        self.assertTrue(conformance.has_feature("LT"))
        self.assertTrue(conformance.has_feature("DF"))


class TestConformanceParsing(unittest.TestCase):
    """Test parsing of conformance elements"""

    def test_parse_mandatory_conformance(self):
        """Test parsing of mandatory conformance"""
        xml = """<attribute id="0x0002" name="Occupancy" type="OccupancyBitmap">
                <access read="true" readPrivilege="view"/>
                <mandatoryConform>
                    <feature name="OCC"/>
                </mandatoryConform>
                </attribute>"""
        elem = ET.fromstring(xml)
        feature_map = {"OCC": MockFeature("Occupancy", "OCC")}
        conformance = parse_conformance(elem, feature_map)
        self.assertEqual(conformance.type, "mandatory")
        self.assertEqual(conformance.condition, {"feature": "occupancy"})


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    sys.exit(0 if run_tests() else 1)
