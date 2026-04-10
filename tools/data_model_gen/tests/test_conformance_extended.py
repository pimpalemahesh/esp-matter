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

"""
Extended tests for conformance system — covers conformance.py, conformance_parser.py,
and conformance_codegen.py areas not covered by existing tests.
"""

import unittest
import sys
import os
from xml.etree.ElementTree import Element, SubElement

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conformance import (
    ConformanceDecision,
    get_conformance_type,
    Choice,
    SUPPORTED_CONFORMANCE_TAGS,
)
from xml_processing.conformance_parser import (
    Conformance,
    parse_conformance,
    parse_choice,
    parse_boolean_term,
    parse_element_reference,
    is_mandatory,
    is_restricted_by_conformance,
    match_conformance_items,
    replace_references,
    get_restricted_tags,
)
from utils import config


# Mock feature for testing
class MockFeature:
    def __init__(self, name, code, func_name=None):
        self.name = name
        self.code = code
        self.func_name = func_name or name.lower()


class TestGetConformanceType(unittest.TestCase):
    """Test get_conformance_type() — all conformance type mappings."""

    def test_mandatory(self):
        self.assertEqual(
            get_conformance_type("mandatoryConform"), ConformanceDecision.MANDATORY
        )
        self.assertEqual(
            get_conformance_type("mandatory"), ConformanceDecision.MANDATORY
        )

    def test_optional(self):
        self.assertEqual(
            get_conformance_type("optionalConform"), ConformanceDecision.OPTIONAL
        )
        self.assertEqual(get_conformance_type("optional"), ConformanceDecision.OPTIONAL)

    def test_otherwise(self):
        self.assertEqual(
            get_conformance_type("otherwiseConform"), ConformanceDecision.OTHERWISE
        )

    def test_deprecated(self):
        self.assertEqual(
            get_conformance_type("deprecateConform"), ConformanceDecision.DEPRECATED
        )
        self.assertEqual(
            get_conformance_type("deprecated"), ConformanceDecision.DEPRECATED
        )

    def test_disallowed(self):
        self.assertEqual(
            get_conformance_type("disallowConform"), ConformanceDecision.DISALLOWED
        )
        self.assertEqual(
            get_conformance_type("disallow"), ConformanceDecision.DISALLOWED
        )

    def test_provisional(self):
        self.assertEqual(
            get_conformance_type("provisionalConform"), ConformanceDecision.PROVISIONAL
        )
        self.assertEqual(
            get_conformance_type("provisional"), ConformanceDecision.PROVISIONAL
        )

    def test_described(self):
        self.assertEqual(
            get_conformance_type("describedConform"), ConformanceDecision.DESCRIBED
        )

    def test_unknown(self):
        self.assertEqual(
            get_conformance_type("unknownConform"), ConformanceDecision.NOT_APPLICABLE
        )


class TestSupportedConformanceTags(unittest.TestCase):
    """Test that all expected conformance tags are in the set."""

    def test_all_tags_present(self):
        expected = {
            "mandatoryConform",
            "optionalConform",
            "otherwiseConform",
            "deprecateConform",
            "disallowConform",
            "provisionalConform",
            "describedConform",
        }
        self.assertEqual(SUPPORTED_CONFORMANCE_TAGS, expected)


class TestChoice(unittest.TestCase):
    """Test Choice dataclass."""

    def test_basic_choice(self):
        c = Choice(marker="a", more=False)
        self.assertEqual(c.marker, "a")
        self.assertFalse(c.more)

    def test_choice_with_more(self):
        c = Choice(marker="b", more=True)
        self.assertEqual(str(c), "b+")

    def test_choice_to_dict(self):
        c = Choice(marker="a", more=True)
        d = c.to_dict()
        self.assertEqual(d["choice"], "a")
        self.assertTrue(d["more"])
        self.assertEqual(d["min"], 1)

    def test_choice_to_dict_no_more(self):
        c = Choice(marker="a", more=False)
        d = c.to_dict()
        self.assertEqual(d["choice"], "a")
        self.assertNotIn("more", d)

    def test_none_marker_to_dict(self):
        c = Choice(marker=None)
        d = c.to_dict()
        self.assertNotIn("choice", d)


class TestParseChoice(unittest.TestCase):
    """Test parse_choice() — XML choice attribute parsing."""

    def test_none_element(self):
        self.assertIsNone(parse_choice(None))

    def test_with_choice(self):
        elem = Element("optionalConform", choice="a")
        c = parse_choice(elem)
        self.assertIsNotNone(c)
        self.assertEqual(c.marker, "a")

    def test_with_more(self):
        elem = Element("optionalConform", choice="a", more="true")
        c = parse_choice(elem)
        self.assertTrue(c.more)

    def test_no_choice_attribute(self):
        elem = Element("optionalConform")
        c = parse_choice(elem)
        self.assertIsNone(c)


class TestGetRestrictedTags(unittest.TestCase):
    """Test get_restricted_tags() — respects provisional mode."""

    def test_default_includes_provisional(self):
        config.setup_provisional_mode(False)
        tags = get_restricted_tags()
        self.assertIn("provisionalConform", tags)
        self.assertIn("disallowConform", tags)
        self.assertIn("deprecateConform", tags)

    def test_provisional_mode_excludes_provisional(self):
        config.setup_provisional_mode(True)
        tags = get_restricted_tags()
        self.assertNotIn("provisionalConform", tags)
        self.assertIn("disallowConform", tags)
        config.setup_provisional_mode(False)  # reset


class TestParseConformance(unittest.TestCase):
    """Test parse_conformance() — main entry point."""

    def test_none_element(self):
        self.assertIsNone(parse_conformance(None, {}))

    def test_mandatory_conformance(self):
        elem = Element("conformance")
        SubElement(elem, "mandatoryConform")
        result = parse_conformance(elem, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.type, ConformanceDecision.MANDATORY)

    def test_optional_conformance(self):
        elem = Element("conformance")
        SubElement(elem, "optionalConform")
        result = parse_conformance(elem, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.type, ConformanceDecision.OPTIONAL)

    def test_deprecated_conformance(self):
        elem = Element("conformance")
        SubElement(elem, "deprecateConform")
        result = parse_conformance(elem, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.type, ConformanceDecision.DEPRECATED)

    def test_disallowed_conformance(self):
        elem = Element("conformance")
        SubElement(elem, "disallowConform")
        result = parse_conformance(elem, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.type, ConformanceDecision.DISALLOWED)

    def test_mandatory_with_feature(self):
        feature_map = {"LT": MockFeature("Lighting", "LT", "lighting")}
        elem = Element("conformance")
        mandatory = SubElement(elem, "mandatoryConform")
        SubElement(mandatory, "feature", name="LT")
        result = parse_conformance(elem, feature_map)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.condition)

    def test_no_matching_tag(self):
        elem = Element("conformance")
        SubElement(elem, "unknownConform")
        result = parse_conformance(elem, {})
        self.assertIsNone(result)


class TestConformanceClass(unittest.TestCase):
    """Test Conformance class methods."""

    def test_get_dependent_features_simple(self):
        conf = Conformance({})
        condition = {"feature": "lighting"}
        features = conf.get_dependent_features(condition)
        self.assertEqual(features, ["lighting"])

    def test_get_dependent_features_and(self):
        conf = Conformance({})
        condition = {"and": [{"feature": "a"}, {"feature": "b"}]}
        features = conf.get_dependent_features(condition)
        self.assertIn("a", features)
        self.assertIn("b", features)

    def test_get_dependent_features_not_excluded(self):
        conf = Conformance({})
        condition = {"not": {"feature": "excluded"}}
        features = conf.get_dependent_features(condition)
        self.assertEqual(features, [])

    def test_get_dependent_features_none(self):
        conf = Conformance({})
        features = conf.get_dependent_features(None)
        self.assertEqual(features, [])

    def test_has_feature(self):
        fm = {"LT": MockFeature("Lighting", "LT", "lighting")}
        conf = Conformance(fm)
        conf.condition = {"feature": "lighting"}
        self.assertTrue(conf.has_feature("LT"))

    def test_has_feature_missing(self):
        fm = {"LT": MockFeature("Lighting", "LT", "lighting")}
        conf = Conformance(fm)
        conf.condition = {"feature": "lighting"}
        self.assertFalse(conf.has_feature("XX"))

    def test_has_feature_no_condition(self):
        fm = {"LT": MockFeature("Lighting", "LT", "lighting")}
        conf = Conformance(fm)
        conf.condition = None
        self.assertFalse(conf.has_feature("LT"))

    def test_to_dict(self):
        fm = {}
        conf = Conformance(fm)
        conf.type = ConformanceDecision.MANDATORY
        conf.condition = {"feature": "lighting"}
        d = conf.to_dict()
        self.assertEqual(d["type"], "mandatory")
        self.assertIn("condition", d)


class TestParseBooleanTerm(unittest.TestCase):
    """Test parse_boolean_term() — AND/OR/NOT parsing."""

    def test_not_term(self):
        elem = Element("notTerm")
        SubElement(elem, "feature", name="LT")
        fm = {"LT": MockFeature("Lighting", "LT", "lighting")}
        result = parse_boolean_term(elem, fm)
        self.assertIn("not", result)

    def test_and_term_single_operand(self):
        elem = Element("andTerm")
        SubElement(elem, "feature", name="LT")
        fm = {"LT": MockFeature("Lighting", "LT", "lighting")}
        result = parse_boolean_term(elem, fm)
        self.assertIn("and", result)
        self.assertIsInstance(result["and"], list)

    def test_and_term_multiple_operands(self):
        elem = Element("andTerm")
        SubElement(elem, "feature", name="LT")
        SubElement(elem, "feature", name="CT")
        fm = {
            "LT": MockFeature("Lighting", "LT", "lighting"),
            "CT": MockFeature("ColorTemp", "CT", "color_temp"),
        }
        result = parse_boolean_term(elem, fm)
        self.assertIn("and", result)
        self.assertEqual(len(result["and"]), 2)

    def test_or_term(self):
        elem = Element("orTerm")
        SubElement(elem, "feature", name="LT")
        SubElement(elem, "feature", name="CT")
        fm = {
            "LT": MockFeature("Lighting", "LT", "lighting"),
            "CT": MockFeature("ColorTemp", "CT", "color_temp"),
        }
        result = parse_boolean_term(elem, fm)
        self.assertIn("or", result)

    def test_empty_not_returns_none(self):
        elem = Element("notTerm")
        result = parse_boolean_term(elem, {})
        self.assertIsNone(result)


class TestParseElementReference(unittest.TestCase):
    """Test parse_element_reference() — feature/attribute/command/condition refs."""

    def test_feature_reference(self):
        elem = Element("feature", name="LT")
        fm = {"LT": MockFeature("Lighting", "LT", "lighting")}
        result = parse_element_reference(elem, fm)
        self.assertIn("feature", result)
        self.assertEqual(result["feature"], "lighting")

    def test_attribute_reference(self):
        elem = Element("attribute", name="OnOff")
        result = parse_element_reference(elem, {})
        self.assertEqual(result, {"attribute": "OnOff"})

    def test_command_reference(self):
        elem = Element("command", name="Toggle")
        result = parse_element_reference(elem, {})
        self.assertEqual(result, {"command": "Toggle"})

    def test_condition_reference(self):
        elem = Element("condition", name="Zigbee")
        result = parse_element_reference(elem, {})
        self.assertEqual(result, {"condition": "Zigbee"})

    def test_unknown_feature_returns_none(self):
        elem = Element("feature", name="UNKNOWN")
        result = parse_element_reference(elem, {})
        self.assertIsNone(result)

    def test_unknown_tag_returns_none(self):
        elem = Element("unknown", name="something")
        result = parse_element_reference(elem, {})
        self.assertIsNone(result)


class TestIsMandatory(unittest.TestCase):
    """Test is_mandatory() — XML conformance mandatory check."""

    def test_mandatory(self):
        elem = Element("conformance")
        SubElement(elem, "mandatoryConform")
        self.assertTrue(is_mandatory(elem))

    def test_not_mandatory(self):
        elem = Element("conformance")
        SubElement(elem, "optionalConform")
        self.assertFalse(is_mandatory(elem))

    def test_otherwise_mandatory(self):
        elem = Element("conformance")
        otherwise = SubElement(elem, "otherwiseConform")
        SubElement(otherwise, "mandatoryConform")
        self.assertTrue(is_mandatory(elem))


class TestIsRestrictedByConformance(unittest.TestCase):
    """Test is_restricted_by_conformance() — element filtering."""

    def test_no_conformance(self):
        elem = Element("attribute", name="test")
        self.assertFalse(is_restricted_by_conformance({}, elem))

    def test_deprecated_element(self):
        elem = Element("attribute", name="test")
        SubElement(elem, "deprecateConform")
        self.assertTrue(is_restricted_by_conformance({}, elem))

    def test_disallowed_element(self):
        elem = Element("attribute", name="test")
        SubElement(elem, "disallowConform")
        self.assertTrue(is_restricted_by_conformance({}, elem))

    def test_zigbee_specific_skipped(self):
        elem = Element("attribute", name="test")
        optional = SubElement(elem, "optionalConform")
        SubElement(optional, "condition", name="Zigbee")
        self.assertTrue(is_restricted_by_conformance({}, elem))

    def test_missing_feature_skipped(self):
        elem = Element("attribute", name="test")
        mandatory = SubElement(elem, "mandatoryConform")
        SubElement(mandatory, "feature", name="MISSING")
        self.assertTrue(is_restricted_by_conformance({}, elem))

    def test_present_feature_not_skipped(self):
        elem = Element("attribute", name="test")
        mandatory = SubElement(elem, "mandatoryConform")
        SubElement(mandatory, "feature", name="LT")
        fm = {"LT": MockFeature("Lighting", "LT")}
        self.assertFalse(is_restricted_by_conformance(fm, elem))


class TestReplaceReferences(unittest.TestCase):
    """Test replace_references() — attribute/command name replacement."""

    def test_attribute_reference(self):
        condition = {"attribute": "OnOff"}
        result = replace_references(condition, {})
        self.assertEqual(result, {"attribute": "OnOff"})

    def test_command_reference_with_map(self):
        condition = {"command": "Toggle"}
        ref_map = {"Toggle": ("0x0002", "COMMAND_FLAG_ACCEPTED")}
        result = replace_references(condition, ref_map)
        self.assertEqual(result["command"], "Toggle")
        self.assertEqual(result["flag"], "COMMAND_FLAG_ACCEPTED")

    def test_nested_condition(self):
        condition = {"and": [{"feature": "a"}, {"feature": "b"}]}
        result = replace_references(condition, {})
        self.assertEqual(len(result["and"]), 2)

    def test_list_condition(self):
        condition = [{"feature": "a"}, {"feature": "b"}]
        result = replace_references(condition, {})
        self.assertEqual(len(result), 2)

    def test_scalar_passthrough(self):
        self.assertEqual(replace_references("test", {}), "test")
        self.assertEqual(replace_references(42, {}), 42)


class TestMatchConformanceItems(unittest.TestCase):
    """Test match_conformance_items() — feature-to-item matching."""

    def test_no_conformance(self):
        class MockItem:
            conformance = None

        feature = MockFeature("Lighting", "LT", "lighting")
        result = match_conformance_items(feature, [MockItem()])
        self.assertEqual(result, [])

    def test_mandatory_match(self):
        class MockItem:
            pass

        item = MockItem()
        fm = {"LT": MockFeature("Lighting", "LT", "lighting")}
        conf = Conformance(fm)
        conf.type = ConformanceDecision.MANDATORY
        conf.condition = {"feature": "lighting"}
        item.conformance = conf
        feature = MockFeature("Lighting", "LT", "lighting")
        result = match_conformance_items(feature, [item])
        self.assertEqual(len(result), 1)

    def test_no_match(self):
        class MockItem:
            pass

        item = MockItem()
        fm = {"CT": MockFeature("ColorTemp", "CT", "color_temp")}
        conf = Conformance(fm)
        conf.type = ConformanceDecision.MANDATORY
        conf.condition = {"feature": "color_temp"}
        item.conformance = conf
        feature = MockFeature("Lighting", "LT", "lighting")
        result = match_conformance_items(feature, [item])
        self.assertEqual(len(result), 0)


class TestConformanceDecision(unittest.TestCase):
    """Test ConformanceDecision enum."""

    def test_to_string(self):
        self.assertEqual(ConformanceDecision.MANDATORY.to_string(), "mandatory")
        self.assertEqual(ConformanceDecision.OPTIONAL.to_string(), "optional")
        self.assertEqual(ConformanceDecision.DISALLOWED.to_string(), "disallowed")
        self.assertEqual(ConformanceDecision.DEPRECATED.to_string(), "deprecated")
        self.assertEqual(ConformanceDecision.PROVISIONAL.to_string(), "provisional")

    def test_all_values_unique(self):
        values = [e.value for e in ConformanceDecision]
        self.assertEqual(len(values), len(set(values)))


if __name__ == "__main__":
    unittest.main()
