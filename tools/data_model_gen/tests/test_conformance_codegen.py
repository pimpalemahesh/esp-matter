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
Comprehensive test suite for conformance code generation.

Tests the conversion of conformance JSON (from XML parsing) to C++ conditional
expressions used in the ESP Matter SDK.
"""

import unittest
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from code_generation.conformance_codegen import (
    Conformance,
    FeatureConformance,
)
from utils.exceptions import CodeGenerationError



class TestBasicCodeGeneration(unittest.TestCase):
    """Test basic conformance to C++ code generation"""

    def test_none_conformance(self):
        """Test that None conformance returns None"""
        result = Conformance(None)()
        self.assertIsNone(result)

    def test_empty_conformance(self):
        """Test that empty dict returns None"""
        result = Conformance({})()
        self.assertIsNone(result)

    def test_no_condition(self):
        """Test conformance with type but no condition"""
        conformance = {"type": "mandatory"}
        result = Conformance(conformance)()
        self.assertIsNone(result)

    def test_no_type(self):
        """Test conformance with condition but no type"""
        conformance = {"condition": {"feature": "lighting"}}
        with self.assertRaises(CodeGenerationError):
            Conformance(conformance)()


class TestFeatureConditions(unittest.TestCase):
    """Test feature-based conformance code generation"""

    def test_single_feature(self):
        """Test single feature with runtime check"""
        conformance = {"type": "mandatory", "condition": {"feature": "lighting"}}
        result = Conformance(conformance)()

        self.assertEqual("feature_map & feature::lighting::get_id()", result)


class TestAttributeConditions(unittest.TestCase):
    """Test attribute-based conformance code generation"""

    def test_attribute_existence_check(self):
        """Test attribute existence condition"""
        conformance = {"type": "mandatory", "condition": {"attribute": "HoldTime"}}
        result = Conformance(conformance)()

        self.assertEqual(
            "esp_matter::attribute::get(cluster, attribute::HoldTime::Id) != nullptr",
            result,
        )


class TestCommandConditions(unittest.TestCase):
    """Test command-based conformance code generation"""

    def test_command_existence_check(self):
        """Test command existence condition"""
        conformance = {
            "type": "mandatory",
            "condition": {"command": "SetHoldTime", "flag": "COMMAND_FLAG_ACCEPTED"},
        }
        result = Conformance(conformance)()

        self.assertEqual(
            "esp_matter::command::get(cluster, command::SetHoldTime::Id, COMMAND_FLAG_ACCEPTED) != nullptr",
            result,
        )

    def test_command_without_flag(self):
        """Test command condition without explicit flag"""
        conformance = {"type": "mandatory", "condition": {"command": "SetHoldTime"}}
        with self.assertRaises(CodeGenerationError):
            Conformance(conformance)()


class TestBooleanOperations(unittest.TestCase):
    """Test AND, OR, NOT operations in code generation"""

    def test_and_two_features(self):
        """Test AND of two features"""
        conformance = {
            "type": "mandatory",
            "condition": {
                "and": [{"feature": "lighting"}, {"feature": "dead_front_behavior"}]
            },
        }
        result = Conformance(conformance)()

        self.assertEqual(
            "((feature_map & feature::lighting::get_id()) && (feature_map & feature::dead_front_behavior::get_id()))",
            result,
        )

    def test_or_two_features(self):
        """Test OR of two features"""
        conformance = {
            "type": "mandatory",
            "condition": {"or": [{"feature": "hue_saturation"}, {"feature": "xy"}]},
        }
        result = Conformance(conformance)()

        self.assertEqual(
            "((feature_map & feature::hue_saturation::get_id()) || (feature_map & feature::xy::get_id()))",
            result,
        )

    def test_not_feature(self):
        """Test NOT of a feature"""
        conformance = {
            "type": "optional",
            "condition": {"not": {"feature": "off_only"}},
        }
        result = Conformance(conformance)()

        self.assertEqual("!(feature_map & feature::off_only::get_id())", result)

    def test_complex_nested_and_or_not(self):
        """Test complex nested: AND(OR(...), NOT(...))"""
        conformance = {
            "type": "mandatory",
            "condition": {
                "and": [
                    {"or": [{"feature": "hs"}, {"feature": "xy"}]},
                    {"not": {"feature": "off_only"}},
                ]
            },
        }
        result = Conformance(conformance)()

        self.assertEqual(
            "((((feature_map & feature::hs::get_id()) || (feature_map & feature::xy::get_id()))) && (!(feature_map & feature::off_only::get_id())))",
            result,
        )


class TestOtherwiseConformance(unittest.TestCase):
    """Test otherwise conformance code generation"""

    def test_otherwise_simple(self):
        """Test otherwise with simple sub-conditions"""
        conformance = {
            "type": "otherwise",
            "condition": {"mandatory": {"feature": "lighting"}, "optional": True},
        }
        result = Conformance(conformance)()

        self.assertEqual("(feature_map & feature::lighting::get_id())", result)

    def test_otherwise_with_deprecated(self):
        """Test otherwise with deprecated sub-condition"""
        conformance = {
            "type": "otherwise",
            "condition": {
                "mandatory": {"feature": "lighting"},
                "deprecate": True,
            },
        }
        result = Conformance(conformance)()

        self.assertEqual("(feature_map & feature::lighting::get_id())", result)

    def test_otherwise_all_true(self):
        """Test otherwise where all sub-conditions are True"""
        conformance = {
            "type": "otherwise",
            "condition": {"mandatory": True, "optional": True},
        }
        result = Conformance(conformance)()

        self.assertIsNone(result)


class TestHasNotCondition(unittest.TestCase):
    """Test has_not_condition helper function"""

    def test_has_not_at_top_level(self):
        """Test detection of NOT at top level"""
        conformance = {
            "type": "optional",
            "condition": {"not": {"feature": "off_only"}},
        }
        self.assertTrue(Conformance(conformance).is_not_term_present)

    def test_no_not_condition(self):
        """Test when there's no NOT condition"""
        conformance = {"type": "mandatory", "condition": {"feature": "lighting"}}
        self.assertFalse(Conformance(conformance).is_not_term_present)

    def test_not_nested_deeper(self):
        """Test NOT nested in AND (not at top level)"""
        conformance = {
            "type": "mandatory",
            "condition": {"and": [{"feature": "a"}, {"not": {"feature": "b"}}]},
        }
        self.assertTrue(FeatureConformance(conformance).is_not_term_present)

    def test_none_conformance(self):
        """Test with None conformance"""
        self.assertFalse(FeatureConformance(None).is_not_term_present)

    def test_no_condition_key(self):
        """Test with conformance missing condition key"""
        self.assertFalse(FeatureConformance({"type": "mandatory"}).is_not_term_present)


class TestFeatureConformanceClass(unittest.TestCase):
    """Test FeatureConformance analysis class"""

    def test_simple_mandatory_feature(self):
        """Test extraction of simple mandatory feature"""
        conformance = {"type": "mandatory", "condition": {"feature": "lighting"}}
        fc = FeatureConformance(conformance)()

        self.assertEqual("feature_map & feature::lighting::get_id()", fc)

    def test_mandatory_parent_feature_name(self):
        """Test extraction of mandatory parent feature name"""
        conformance = {
            "type": "otherwise",
            "condition": {"mandatory": {"feature": "lighting"}, "optional": True},
        }
        fc = FeatureConformance(conformance)

        self.assertEqual("lighting", fc.mandatory_parent)

    def test_exact_one_feature_detection(self):
        """Test detection of 'exactly one' choice conformance"""
        conformance = {"type": "optional", "choice": "a"}
        fc = FeatureConformance(conformance)
        self.assertTrue(fc.is_exact_one())

    def test_at_least_one_feature_detection(self):
        """Test detection of 'at least one' choice conformance"""
        conformance = {"type": "optional", "choice": "a", "more": True, "min": 1}
        fc = FeatureConformance(conformance)

        self.assertTrue(fc.is_at_least_one())
        self.assertFalse(fc.is_exact_one())


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_invalid_condition_type(self):
        """Test with invalid condition type (not a dict)"""
        conformance = {"type": "mandatory", "condition": "invalid"}
        with self.assertRaises(AttributeError):
            Conformance(conformance)()

    def test_empty_and_list(self):
        """Test AND with empty list"""
        conformance = {"type": "mandatory", "condition": {"and": []}}
        result = Conformance(conformance)()

        self.assertIsNone(result)

    def test_empty_or_list(self):
        """Test OR with empty list"""
        conformance = {"type": "mandatory", "condition": {"or": []}}
        result = Conformance(conformance)()

        self.assertIsNone(result)

    def test_single_element_and(self):
        """Test AND with single element"""
        conformance = {
            "type": "mandatory",
            "condition": {"and": [{"feature": "lighting"}]},
        }
        result = Conformance(conformance)()

        self.assertIsNotNone(result)
        # Should not have && operator for single element
        self.assertNotIn("&&", result)

    def test_single_element_or(self):
        """Test OR with single element"""
        conformance = {
            "type": "mandatory",
            "condition": {"or": [{"feature": "lighting"}]},
        }
        result = Conformance(conformance)()

        self.assertIsNotNone(result)
        # Should not have || operator for single element
        self.assertNotIn("||", result)

    def test_and_with_none_subconditions(self):
        """Test AND where some subconditions are invalid"""
        conformance = {
            "type": "mandatory",
            "condition": {"and": [{"feature": "lighting"}, {"invalid": "data"}]},
        }
        result = Conformance(conformance)()

        # Should still generate code for valid subcondition
        self.assertIsNotNone(result)
        self.assertIn("feature::lighting::get_id()", result)


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
