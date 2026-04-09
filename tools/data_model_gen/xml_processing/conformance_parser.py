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

import logging
from utils.helper import convert_to_snake_case, safe_get_attr
from xml.etree.ElementTree import Element
from utils.conformance import (
    get_conformance_type,
    ConformanceTAG,
    ConformanceDecision,
    BaseConformance,
    Choice,
    SUPPORTED_CONFORMANCE_TAGS,
)
from typing import Optional
from utils import config

logger = logging.getLogger(__name__)

# XML tag constants
OTHERWISE_CONFORM = "otherwiseConform"
OPTIONAL_CONFORM = "optionalConform"
PROVISIONAL_CONFORM = "provisionalConform"
MANDATORY_CONFORM = "mandatoryConform"
DEPRECATE_CONFORM = "deprecateConform"
DISALLOW_CONFORM = "disallowConform"


BOOLEAN_TERMS = {
    "andTerm": ConformanceTAG.AND.value,
    "orTerm": ConformanceTAG.OR.value,
    "notTerm": ConformanceTAG.NOT.value,
}


def get_restricted_tags():
    if config.allow_provisional():
        return {
            DISALLOW_CONFORM,
            DEPRECATE_CONFORM,
        }
    return {
        DISALLOW_CONFORM,
        DEPRECATE_CONFORM,
        PROVISIONAL_CONFORM,
    }


def parse_choice(choice_elem: Element) -> Optional[Choice]:
    if choice_elem is None:
        return None
    marker = choice_elem.get("choice")
    more = choice_elem.get("more", "").lower() == "true"
    if marker is not None:
        return Choice(marker, more)
    return None


class Conformance(BaseConformance):
    """
    Base class representing conformance requirements for Matter Data Model elements.
    """

    condition: dict = None
    feature_map: dict = None
    more: bool = None
    min: int = None

    def __init__(self, feature_map: dict):
        self.feature_map = feature_map

    def parse(self, conformance_elem: Element):
        if conformance_elem is None:
            return None

        self.type = get_conformance_type(conformance_elem.tag)
        if self.type == ConformanceDecision.OTHERWISE:
            self.condition = self._parse_otherwise_conformance(conformance_elem)
        else:
            self.choice = parse_choice(conformance_elem)
            self.condition = self._parse_common_conformance(conformance_elem)
        return self

    def _parse_otherwise_conformance(self, conformance_elem: Element):
        sub_conditions = {}
        for child in conformance_elem:
            if child.tag not in SUPPORTED_CONFORMANCE_TAGS:
                continue
            child_type = get_conformance_type(child.tag).to_string()
            sub_condition = self._build_sub_condition(child, child_type)
            self._add_to_conditions(sub_conditions, child_type, sub_condition)
        return sub_conditions

    def _build_sub_condition(self, child: Element, child_type: str) -> dict:
        """Build a sub-condition from a conformance child element."""
        sub_condition = {}
        if child_type == ConformanceDecision.OPTIONAL.to_string():
            choice = parse_choice(child)
            if choice:
                sub_condition.update(choice.to_dict())
        parsed = self._parse_common_conformance(child)
        if parsed:
            if isinstance(parsed, dict):
                sub_condition.update(parsed)
            else:
                sub_condition["condition"] = parsed
        return sub_condition

    def _add_to_conditions(self, conditions: dict, key: str, value) -> None:
        """Add a condition value, converting to list if key already exists."""
        value = value if value else True
        if key in conditions:
            existing = conditions[key]
            conditions[key] = (
                [existing, value]
                if not isinstance(existing, list)
                else existing + [value]
            )
        else:
            conditions[key] = value

    def _parse_common_conformance(self, parent_elem: Element):
        conditions = parse_children(parent_elem, self.feature_map)

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {ConformanceTAG.AND.value: conditions}

    def get_dependent_features(self, condition: dict):
        """
        Get all features on which the condition depends.
        NOTE: `not` term indicates that condition is not dependent on that feature.
        """
        features = []
        if isinstance(condition, dict):
            feature = condition.get(ConformanceTAG.FEATURE.value)
            if feature:
                features.append(feature)
            for key, value in condition.items():
                if key == ConformanceTAG.NOT.value:
                    continue
                features.extend(self.get_dependent_features(value))
        elif isinstance(condition, list):
            for item in condition:
                features.extend(self.get_dependent_features(item))

        return features

    def has_feature(self, feature_code):
        """Check if conformance involves a specific feature."""
        if not self.condition:
            return False
        feature_obj = self.feature_map.get(feature_code)
        feature_name = getattr(feature_obj, "func_name", None) if feature_obj else None
        if not feature_name:
            return False
        return feature_name in self.get_dependent_features(self.condition)

    def is_disallowed(self):
        """Check if the conformance is disallowed or depends on unavailable features."""
        if self.type in get_restricted_tags():
            return True
        features = self.get_dependent_features(self.condition)
        return any(feature not in self.feature_map for feature in features)

    def to_dict(self, attribute_map={}):
        result = {"type": self.type.to_string()}

        if self.condition:
            result["condition"] = replace_references(self.condition, attribute_map)

        if self.choice:
            result.update(self.choice.to_dict())

        return result


def is_mandatory(conformance_elem: Element) -> bool:
    """Check if conformance is mandatory."""
    mandatory_conform = conformance_elem.find("mandatoryConform")
    if mandatory_conform is not None:
        return True
    otherwise_mandatory = conformance_elem.find("otherwiseConform/mandatoryConform")
    if otherwise_mandatory is not None:
        return (
            len(otherwise_mandatory) == 0
            or otherwise_mandatory.find("greaterTerm") is not None
        )
    return False


def replace_references(condition, reference_map):
    """
    Replace attribute and command names with their IDs in the reference map.
    """
    if isinstance(condition, dict):
        attr_name = condition.get(ConformanceTAG.ATTRIBUTE.value)
        if attr_name:
            return {ConformanceTAG.ATTRIBUTE.value: attr_name}
        cmd_name = condition.get(ConformanceTAG.COMMAND.value)
        if cmd_name and cmd_name in reference_map:
            cmd_data = reference_map.get(cmd_name)
            if isinstance(cmd_data, tuple) and len(cmd_data) == 2:
                return {
                    ConformanceTAG.COMMAND.value: cmd_name,
                    ConformanceTAG.COMMAND_FLAG.value: cmd_data[1],
                }
            else:
                return {ConformanceTAG.COMMAND.value: cmd_name}
        return {
            key: replace_references(value, reference_map)
            for key, value in condition.items()
        }
    elif isinstance(condition, list):
        return [replace_references(item, reference_map) for item in condition]
    return condition


def parse_conformance(conformance_elem, feature_map):
    """Parse conformance from XML; single entry point for attaching conformance to cluster elements."""
    if conformance_elem is None:
        return None
    for tag in SUPPORTED_CONFORMANCE_TAGS:
        conformance = conformance_elem.find(tag)
        if conformance is not None:
            return Conformance(feature_map).parse(conformance)
    logger.debug(f"Unknown conformance tag for element {conformance_elem}")
    return None


def parse_children(parent_elem, feature_map):
    return [
        parsed
        for child in parent_elem
        if (parsed := parse_condition(child, feature_map))
    ]


def parse_condition(elem, feature_map):
    """
    Parse any condition element.
    """
    if elem.tag in BOOLEAN_TERMS:
        return parse_boolean_term(elem, feature_map)
    return parse_element_reference(elem, feature_map)


def parse_boolean_term(term_elem, feature_map):
    """
    Parse a boolean terms.
    NOTE: Greater and Equal terms are not supported as no use in esp-matter.
    """
    term_type = BOOLEAN_TERMS[term_elem.tag]
    operands = parse_children(term_elem, feature_map)

    if term_type == ConformanceTAG.NOT.value:
        return {term_type: operands[0]} if operands else None

    if term_type in (ConformanceTAG.AND.value, ConformanceTAG.OR.value):
        return {term_type: operands} if operands else None

    return None

def parse_element_reference(ref_elem, feature_map):
    """
    Parse a reference to a feature, attribute, command, or condition.
    """
    if ref_elem.tag == ConformanceTAG.ATTRIBUTE.value:
        return {ConformanceTAG.ATTRIBUTE.value: ref_elem.get("name")}

    elif ref_elem.tag == ConformanceTAG.COMMAND.value:
        return {ConformanceTAG.COMMAND.value: ref_elem.get("name")}

    elif ref_elem.tag == ConformanceTAG.FEATURE.value:
        feature_code = ref_elem.get("name")
        if feature_code in feature_map:
            feature_name = convert_to_snake_case(feature_map[feature_code].name)
            return {ConformanceTAG.FEATURE.value: feature_name}
        else:
            logger.warning(f"Feature {feature_code} not found in feature map")
            return None

    elif ref_elem.tag == ConformanceTAG.CONDITION.value:
        return {ConformanceTAG.CONDITION.value: ref_elem.get("name")}

    return None


def is_restricted_by_conformance(feature_map, element):
    """
    Check if the conformance is provisional, deprecated, disallowed or if depends on any disallowed feature.

    Args:
        feature_map: The feature map
        element: The element from the cluster XML file

    Returns:
        True if the element should be skipped, False otherwise
    """
    conformance_element = None
    for elem in element.iter():
        if elem.tag.endswith("Conform"):
            conformance_element = elem
            break

    if conformance_element is None:
        return False

    element_name = element.get("name", "Unknown")

    if conformance_element.tag in get_restricted_tags():
        logger.debug(
            f"Skipping - {conformance_element.tag} conformance for element {element_name}"
        )
        return True

    if conformance_element.tag == OTHERWISE_CONFORM:
        first_child = next(iter(conformance_element), None)
        if first_child is not None:
            if first_child.tag == MANDATORY_CONFORM:
                # Check if all required features exist in feature map
                feature_list = first_child.findall(".//feature")
                for feature in feature_list:
                    feature_name = feature.get("name")
                    if feature_name not in feature_map:
                        return True
                return False
            elif first_child.tag in get_restricted_tags():
                return True

    # Check for Zigbee-specific optional conformance
    condition = conformance_element.find("condition")
    if condition is not None:
        zigbee_condition = condition.get("name")
        if zigbee_condition and zigbee_condition.lower() == "zigbee":
            logger.debug(f"Skipping - Zigbee specific element {element_name}")
            return True

    # Checks if conformance depends on features that are not in feature map
    all_features_list = conformance_element.findall(".//feature")
    for feature in all_features_list:
        feature_name = feature.get("name")
        if feature_name and feature_name not in feature_map:
            logger.debug(
                f"Skipping - feature {feature_name} not in feature map for element {element_name}"
            )
            return True
    return False


def match_conformance_items(feature, item_list):
    """
    Get list of items matched with current feature.

    This finds all items (attributes, commands, events) that have a mandatory
    conformance relationship with the given feature.

    Args:
        feature: Feature object to match against
        item_list: List of items to check for match

    Returns:
        A list of items that have conformance with the given feature
    """
    matched_items = []
    for item in item_list:
        conformance = safe_get_attr(item, "conformance")
        if not conformance:
            continue

        if (
            conformance.type == ConformanceDecision.MANDATORY
            and conformance.has_feature(feature.code)
        ):
            matched_items.append(item)
        if (
            conformance.type == ConformanceDecision.OTHERWISE
            and conformance.condition
            and conformance.condition.get("mandatory", False)
            and conformance.has_feature(feature.code)
        ):
            matched_items.append(item)

    return matched_items
