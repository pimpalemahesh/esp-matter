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

import logging
from utils.helper import convert_to_snake_case, safe_get_attr
from xml.etree.ElementTree import Element

logger = logging.getLogger(__name__)

# XML tag constants
OTHERWISE_CONFORM = "otherwiseConform"
OPTIONAL_CONFORM = "optionalConform"
PROVISIONAL_CONFORM = "provisionalConform"
MANDATORY_CONFORM = "mandatoryConform"
DEPRECATE_CONFORM = "deprecateConform"
DISALLOW_CONFORM = "disallowConform"
TOP_LEVEL_CONFORMANCE_TAGS = {
    OTHERWISE_CONFORM,
    OPTIONAL_CONFORM,
    PROVISIONAL_CONFORM,
    MANDATORY_CONFORM,
    DEPRECATE_CONFORM,
    DISALLOW_CONFORM,
}

AND_TERM = "andTerm"
OR_TERM = "orTerm"
NOT_TERM = "notTerm"
GREATER_TERM = "greaterTerm"
EQUAL_TERM = "equalTerm"

NOT_TAG = "not"
AND_TAG = "and"
OR_TAG = "or"
FEATURE_TAG = "feature"
ATTRIBUTE_TAG = "attribute"
COMMAND_TAG = "command"
COMMAND_FLAG_TAG = "flag"
CONDITION_TAG = "condition"
GREATER_TAG = "greater"
EQUAL_TAG = "equal"
LITERAL_TAG = "literal"


class Conformance:
    """
    Base class representing conformance requirements for Matter Data Model elements.
    """

    type: str = None
    condition: dict = None
    feature_map: dict = None
    choice: dict = None
    more: bool = None
    min: int = None

    def __init__(self, feature_map: dict = {}):
        self.feature_map = feature_map

    def parse(self, conformance_elem: Element):
        if conformance_elem is None:
            logger.debug("No conformance element provided")
            return None

        self.type = conformance_elem.tag.replace("Conform", "").lower()
        if self.type == "otherwise":
            sub_conditions = {}
            for child in conformance_elem:
                if child.tag in TOP_LEVEL_CONFORMANCE_TAGS:
                    child_type = child.tag.replace("Conform", "")
                    sub_condition = {}

                    if child.tag == OPTIONAL_CONFORM:
                        if child.get("choice"):
                            sub_condition["choice"] = child.get("choice")
                        if child.get("more"):
                            sub_condition["more"] = child.get("more").lower() == "true"
                        if child.get("min"):
                            try:
                                sub_condition["min"] = int(child.get("min"))
                            except (ValueError, TypeError):
                                logger.warning(
                                    f"Invalid min value in nested optionalConform: {child.get('min')}"
                                )
                                sub_condition["min"] = child.get("min")

                    parsed_condition = parse_condition_element(child, self.feature_map)
                    if parsed_condition:
                        if isinstance(parsed_condition, dict):
                            sub_condition.update(parsed_condition)
                        else:
                            sub_condition["condition"] = parsed_condition

                    if sub_conditions.get(child_type) is not None:
                        child_list = []
                        child_list.append(sub_conditions[child_type])
                        child_list.append(sub_condition if sub_condition else True)
                        sub_conditions[child_type] = child_list
                    else:
                        sub_conditions[child_type] = (
                            sub_condition if sub_condition else True
                        )

            self.condition = sub_conditions if sub_conditions else None
        elif self.type == "optional":
            self.set_optional_choice_elements(conformance_elem)
            self.condition = parse_condition_element(conformance_elem, self.feature_map)
        else:
            self.condition = parse_condition_element(conformance_elem, self.feature_map)
        return self

    def set_optional_choice_elements(self, conformance_elem: Element):
        if conformance_elem.get("choice"):
            self.choice = conformance_elem.get("choice")
        if conformance_elem.get("more"):
            self.more = conformance_elem.get("more").lower() == "true"
        if conformance_elem.get("min"):
            try:
                self.min = int(conformance_elem.get("min"))
            except (ValueError, TypeError):
                logger.warning(
                    f"Invalid min value in optionalConform: {conformance_elem.get('min')}"
                )
                self.min = conformance_elem.get("min")

    def to_dict(self, attribute_map={}):
        """
        Conformance object to dictionary representation.
        """
        result = {"type": self.type}

        if self.condition:
            result["condition"] = replace_references(self.condition, attribute_map)

        if self.choice:
            result["choice"] = self.choice
        if self.more is not None:
            result["more"] = self.more
        if self.min is not None:
            result["min"] = self.min

        return result

    def has_feature(self, feature_code):
        """
        Check if conformance involves a specific feature.

        Args:
            feature_code: The feature code to check for

        Returns:
            True if the feature is referenced in the conformance condition
        """
        if not self.condition:
            return False
        feature_name = (
            self.feature_map.get(feature_code, {}).func_name
            if hasattr(self.feature_map.get(feature_code, {}), "func_name")
            else None
        )
        if not feature_name:
            return False
        return condition_has_feature(self.condition, feature_name)


def replace_references(condition, reference_map):
    """
    Replace attribute and command names with their IDs in the reference map.
    """
    if isinstance(condition, dict):
        attr_name = condition.get(ATTRIBUTE_TAG)
        if attr_name and attr_name in reference_map:
            return {ATTRIBUTE_TAG: attr_name}
        cmd_name = condition.get(COMMAND_TAG)
        if cmd_name and cmd_name in reference_map:
            cmd_data = reference_map.get(cmd_name)
            if isinstance(cmd_data, tuple):
                return {COMMAND_TAG: cmd_name, COMMAND_FLAG_TAG: cmd_data[1]}
            else:
                return {COMMAND_TAG: cmd_name}
        return {
            key: replace_references(value, reference_map)
            for key, value in condition.items()
        }
    elif isinstance(condition, list):
        return [replace_references(item, reference_map) for item in condition]
    return condition


def condition_has_feature(condition, feature_code):
    """
    Check if condition references a specific feature.
    """
    if isinstance(condition, dict):
        if FEATURE_TAG in condition and condition.get(FEATURE_TAG) == feature_code:
            return True

        for key, value in condition.items():
            if key == NOT_TAG:
                # Skip negated features - they don't require the feature
                if isinstance(value, dict):
                    value = value.get(FEATURE_TAG)
                    if value and value == feature_code:
                        continue
            elif isinstance(value, (dict, list)):
                if condition_has_feature(value, feature_code):
                    return True

    elif isinstance(condition, list):
        for item in condition:
            if condition_has_feature(item, feature_code):
                return True
    return False


def parse_conformance(conformance_elem, feature_map):
    """
    Parse a conformance element from XML into a Conformance object.
    Args:
        conformance_elem: The XML element containing conformance information
        feature_map: Dictionary mapping feature codes to feature objects

    Returns:
        Conformance object representing the parsed conformance, or None if invalid
    """
    if conformance_elem is None:
        return None
    mandatory_conform = conformance_elem.find("mandatoryConform")
    optional_conform = conformance_elem.find("optionalConform")
    otherwise_conform = conformance_elem.find("otherwiseConform")

    if mandatory_conform is not None:
        return Conformance(feature_map).parse(mandatory_conform)
    elif optional_conform is not None:
        return Conformance(feature_map).parse(optional_conform)
    elif otherwise_conform is not None:
        return Conformance(feature_map).parse(otherwise_conform)


def parse_condition_element(parent_elem, feature_map):
    """
    Parse condition elements within a conformance element.
    """
    conditions = []

    for child in parent_elem:
        if child.tag in [AND_TERM, OR_TERM, NOT_TERM, GREATER_TERM, EQUAL_TERM]:
            parsed = parse_boolean_term(child, feature_map)
            if parsed:
                conditions.append(parsed)
        elif child.tag in [FEATURE_TAG, ATTRIBUTE_TAG, COMMAND_TAG, CONDITION_TAG]:
            parsed = parse_element_reference(child, feature_map)
            if parsed:
                conditions.append(parsed)

    if len(conditions) > 1:
        return {AND_TAG: conditions}
    elif len(conditions) == 1:
        return conditions[0]

    return None


def parse_boolean_term(term_elem, feature_map):
    """
    Parse a boolean terms.
    NOTE: Supported terms AND, OR, NOT, GREATER, EQUAL.
    """
    term_type = term_elem.tag.replace("Term", "").lower()

    if term_type in [AND_TAG, OR_TAG]:
        subconditions = []
        for child in term_elem:
            subcondition = parse_condition_common(child, feature_map)
            if subcondition:
                subconditions.append(subcondition)

        if len(subconditions) > 1:
            return {term_type: subconditions}
        elif len(subconditions) == 1:
            return {term_type: subconditions[0]}
        return None

    elif term_type == NOT_TAG:
        for child in term_elem:
            subcondition = parse_condition_common(child, feature_map)
            if subcondition:
                return {term_type: subcondition}
        return None

    elif term_type in [GREATER_TAG, EQUAL_TAG]:
        operands = []
        for child in term_elem:
            operand = parse_condition_common(child, feature_map)
            if operand:
                operands.append(operand)

        if len(operands) == 2:
            return {term_type: operands}
        return None

    return None


def parse_condition_common(elem, feature_map):
    """
    Parse any condition element.
    """
    if elem.tag in [AND_TERM, OR_TERM, NOT_TERM, GREATER_TERM, EQUAL_TERM]:
        return parse_boolean_term(elem, feature_map)
    elif elem.tag in [
        FEATURE_TAG,
        ATTRIBUTE_TAG,
        COMMAND_TAG,
        CONDITION_TAG,
        LITERAL_TAG,
    ]:
        return parse_element_reference(elem, feature_map)
    return None


def parse_element_reference(ref_elem, feature_map):
    """
    Parse a reference to a feature, attribute, command, or condition.
    """
    if ref_elem.tag == ATTRIBUTE_TAG:
        return {ATTRIBUTE_TAG: ref_elem.get("name")}

    elif ref_elem.tag == COMMAND_TAG:
        return {COMMAND_TAG: ref_elem.get("name")}

    elif ref_elem.tag == FEATURE_TAG:
        feature_code = ref_elem.get("name")
        if feature_code in feature_map:
            feature_name = convert_to_snake_case(feature_map[feature_code].name)
            return {FEATURE_TAG: feature_name}
        else:
            logger.warning(f"Feature {feature_code} not found in feature map")
            return None

    elif ref_elem.tag == CONDITION_TAG:
        return {CONDITION_TAG: ref_elem.get("name")}

    elif ref_elem.tag == LITERAL_TAG:
        return {LITERAL_TAG: ref_elem.get("value")}

    return None


def check_conformance_restrictions(feature_map, element):
    """
    Check if any conformance restrictions should cause an element to be skipped.

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
        logger.debug(
            f"No conformance element found for element {element.get('name', 'Unknown')}"
        )
        return False

    element_name = element.get("name", "Unknown")

    if conformance_element.tag in [
        DISALLOW_CONFORM,
        DEPRECATE_CONFORM,
        PROVISIONAL_CONFORM,
    ]:
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
            elif first_child.tag in [
                PROVISIONAL_CONFORM,
                DEPRECATE_CONFORM,
                DISALLOW_CONFORM,
            ]:
                return True

    # Check for Zigbee-specific optional conformance
    if conformance_element.tag == OPTIONAL_CONFORM:
        cond = conformance_element.find("condition")
        if cond is not None and cond.get("name", "").lower() == "zigbee":
            logger.debug(f"Skipping - Zigbee specific element {element_name}")
            return True

    # Check if all referenced features exist in feature map
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

        # Check if item is mandatory when this feature is present
        if conformance.type == "mandatory" and conformance.has_feature(feature.code):
            matched_items.append(item)
        # Check otherwise conformance with mandatory sub-condition
        if (
            conformance.type == "otherwise"
            and conformance.condition
            and conformance.condition.get("mandatory", False)
            and conformance.has_feature(feature.code)
        ):
            matched_items.append(item)

    return matched_items
