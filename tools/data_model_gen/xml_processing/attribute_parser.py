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
from .conformance_parser import check_conformance_restrictions, parse_conformance
from .elements import Attribute
from .elements import Cluster
from utils.attribute_type import attribute_type_map
from utils.helper import check_valid_id
from utils.helper import safe_get_attr
from typing import List, Optional
from utils.exceptions import should_skip_internally_managed_flag

logger = logging.getLogger(__name__)


class AttributeParser:
    """Class for parsing attribute data"""

    def __init__(
        self,
        cluster: Cluster,
        feature_map: dict,
        managed_attributes: dict,
        allowed_attributes_ids: list = [],
    ):
        """Initialize the AttributeParser"""
        self.cluster = cluster
        self.feature_map = feature_map if feature_map else {}
        self.processed_attrs = set()
        self.managed_attributes = managed_attributes if managed_attributes else {}
        self.allowed_attributes_ids = (
            allowed_attributes_ids if allowed_attributes_ids else []
        )

    def parse(self, root, base_attributes: List[Attribute] = None):
        """Iterate over all attributes in the cluster and create Attribute objects.

        :param root: The root element of the cluster XML file.
        :param base_attributes: The base attributes.
        :param base_attributes: list[Attribute]:  (Default value = None)

        """
        logger.debug(f"Parsing attributes for cluster {safe_get_attr(self.cluster, 'name')}")
        for attribute in root.findall("attributes/attribute"):
            if not self._should_process_attribute(attribute, base_attributes):
                continue
            logger.debug(f"Processing attribute {attribute.get('name')}")
            attr = self._create_attribute(attribute)
            self._process_attribute_internally_managed(attr)
            self._process_attribute_access(attr, attribute)
            attr.conformance = parse_conformance(attribute, self.feature_map)
            self._get_attribute_min_max_value(attr, attribute)
            logger.debug(f"Attribute {safe_get_attr(attr, 'name')} min value: {attr.min_value} max value: {attr.max_value}")

            # Attribute type exceptions for certain attributes in certain clusters
            if self.cluster.func_name in attribute_type_map.keys():
                if attr.func_name in attribute_type_map[self.cluster.func_name].keys():
                    attr.type = attribute_type_map[self.cluster.func_name][
                        attr.func_name
                    ]["type"]
                    attr.min_value = attribute_type_map[self.cluster.func_name][
                        attr.func_name
                    ]["min"]
                    attr.max_value = attribute_type_map[self.cluster.func_name][
                        attr.func_name
                    ]["max"]
            self.cluster.attributes.add(attr)

        # Add base attributes to the cluster if they are not already in the cluster
        if base_attributes:
            for base_attribute in base_attributes:
                if base_attribute.name not in self.processed_attrs:
                    self.cluster.attributes.add(base_attribute)

        logger.debug(
            f"Processed {len(self.cluster.attributes)} attributes for cluster {safe_get_attr(self.cluster, 'name')}"
        )

    def _should_process_attribute(
        self, attribute, base_attributes: Optional[List[Attribute]] = None
    ):
        """Check if attribute should be processed or not.

        :param attribute:
        :param base_attributes: list[Attribute]:  (Default value = None)
        :returns: True if the attribute should be processed, False otherwise.

        """
        base_attribute = None
        attribute_name = attribute.get("name")
        if not attribute_name:
            logger.debug(f"Skipping - missing attribute name {attribute}")
            return False
        if attribute_name in self.processed_attrs:
            logger.debug(
                f"Skipping - attribute already exists in processed attributes {attribute_name}"
            )
            return False
        self.processed_attrs.add(attribute_name)
        if base_attributes:
            base_attribute = next(
                (
                    attr
                    for attr in base_attributes
                    if attr.name == attribute.get("name")
                ),
                None,
            )
            if not attribute.get("id") and base_attribute:
                attribute.set("id", base_attribute.id)
            if not attribute.get("type") and base_attribute:
                attribute.set("type", base_attribute.type)

        attribute_id = attribute.get("id")

        if not check_valid_id(attribute_id):
            return False
        if not (attribute_name and attribute_id):
            logger.debug(
                f"Skipping - missing name or id or type {attribute_name} {attribute_id}"
            )
            return False

        if (
            self.allowed_attributes_ids
            and int(attribute_id, 16) not in self.allowed_attributes_ids
        ):
            logger.debug(
                f"Skipping - attribute {attribute_name} id {int(attribute_id, 16)} not in allowed attributes"
            )
            return False

        if attribute_name in [safe_get_attr(a, "name") for a in self.processed_attrs]:
            logger.debug(
                f"Skipping - attribute already exists in processed attributes {attribute_name}"
            )
            return False

        if check_conformance_restrictions(self.feature_map, attribute):
            logger.debug(
                f"Skipping - attribute {attribute.get('name', 'unknown')} due to conformance restrictions"
            )
            return False

        return True

    def _create_attribute(self, attribute):
        """Create an Attribute object from XML data

        :param attribute:
        :returns: The created Attribute object.

        """
        attribute_name = attribute.get("name")
        attribute_code = attribute.get("id")

        attribute_type = self._get_attribute_type(attribute)
        mandatory_conform = attribute.find("mandatoryConform")
        otherwise_conform = attribute.find("otherwiseConform")
        # attribute is mandatory if it has mandatory conform with or without <greaterTerm> child element and no other child elements in case of otherwise conform.
        have_mandatory_conform = True if mandatory_conform is not None else False
        otherwise_mandatory_conform = otherwise_conform.find("mandatoryConform") if otherwise_conform else None
        if otherwise_mandatory_conform:
            have_mandatory_conform = len(otherwise_mandatory_conform) == 0 or otherwise_mandatory_conform.find("greaterTerm") is not None

        return Attribute(
            name=attribute_name,
            id=attribute_code,
            type_=attribute_type,
            is_mandatory=have_mandatory_conform,
            access=self._parse_access(attribute.find("access")),
            quality=self._parse_quality(attribute.find("quality")),
            constraint=self._parse_constraint(attribute.find("constraint")),
            default_value=attribute.get("default"),
        )

    def _get_attribute_type(self, attribute):
        """Get attribute type from XML

        :param attribute:
        :returns: The attribute type after processing.

        """
        attribute_type = attribute.get("type")
        if attribute_type is None:
            raise ValueError(f"Attribute type is None for {attribute}")

        # This is to remove the suffix from the attribute type if any
        attribute_type = attribute_type.split(" ")[0].lower()

        attribute_type_from_xml = self.cluster.attribute_types.get(attribute_type, None)
        if attribute_type_from_xml is None:
            attribute_type = self._handle_unknown_type(attribute_type)
        else:
            attribute_type = attribute_type_from_xml
        attribute_type = self._update_attribute_type_by_default_value(
            attribute, attribute_type
        )
        return attribute_type

    def _process_attribute_internally_managed(self, attr):
        """Process the internally managed attribute

        :param attr: The attribute object to process.
        """
        if should_skip_internally_managed_flag(self.cluster.esp_name, attr.func_name):
            attr.internally_managed = False
            return
        elif safe_get_attr(attr, "name", "").lower() in self.managed_attributes:
            attr.internally_managed = True
        elif attr.type == "list":
            attr.internally_managed = True
        else:
            attr.internally_managed = False

    def _process_attribute_access(self, attr, attribute):
        """Process attribute access information from XML

        :param attr: The attribute object to process.
        :param attribute: The attribute element from the cluster XML file.

        """
        access_elem = attribute.find("access")
        if access_elem is None:
            logger.debug("No access element found for attribute")
            return None

        attr.access = Attribute.Access(
            read=access_elem.get("read", "false"),
            readPrivilege=access_elem.get("readPrivilege", None),
            write=access_elem.get("write", "false"),
            writePrivilege=access_elem.get("writePrivilege", None),
        )

    def _parse_access(self, access_elem):
        """Parse access information from XML

        :param access_elem:
        :returns: The parsed access information.

        """
        if access_elem is None:
            logger.debug("No access element found for attribute")
            return None

        return Attribute.Access(
            read=access_elem.get("read", "false"),
            readPrivilege=access_elem.get("readPrivilege", None),
            write=access_elem.get("write", "false"),
            writePrivilege=access_elem.get("writePrivilege", None),
        )

    def _parse_quality(self, quality_elem):
        """Parse quality information from XML

        :param quality_elem:
        :returns: The parsed quality information.

        """
        if quality_elem is None:
            logger.debug("No quality element found for attribute")
            return None

        changeOmitted = quality_elem.get("changeOmitted", "false")
        nullable = quality_elem.get("nullable", "false")
        scene = quality_elem.get("scene", "false")
        persistence = quality_elem.get("persistence", "")
        reportable = quality_elem.get("reportable", "false")
        sourceAttribution = quality_elem.get("sourceAttribution", "false")
        quieterReporting = quality_elem.get("quieterReporting", "false")

        return Attribute.Quality(
            changeOmitted=changeOmitted,
            nullable=nullable,
            scene=scene,
            persistence=persistence,
            reportable=reportable,
            sourceAttribution=sourceAttribution,
            quieterReporting=quieterReporting,
        )

    def _parse_constraint(self, constraint_elem):
        """Parse constraint information from XML

        :param constraint_elem:
        :returns: The parsed constraint information.

        """
        if constraint_elem is None:
            logger.debug("No constraint element found for attribute")
            return None

        constraint_type = None
        constraint_value = None
        from_value = None
        to_value = None

        for child in constraint_elem:
            if child.tag == "maxLength":
                constraint_type = "maxLength"
                constraint_value = child.get("value", "")
            elif child.tag == "min":
                constraint_type = "min"
                constraint_value = child.get("value", "")
            elif child.tag == "max":
                constraint_type = "max"
                constraint_value = child.get("value", "")
            elif child.tag == "between":
                constraint_type = "between"
                from_elem = child.find("from")
                to_elem = child.find("to")

                if from_elem is not None:
                    from_value = from_elem.get("value", "")
                else:
                    from_value = "0"

                if to_elem is not None:
                    to_value = to_elem.get("value", "")
                else:
                    to_value = "0"
            elif child.tag == "desc":
                constraint_type = "desc"
                desc_text = child.text if child.text else ""
                if desc_text and desc_text.strip():
                    constraint_value = desc_text.strip()

        if constraint_type == "between":
            return Attribute.Constraint(
                type=constraint_type, from_=from_value, to_=to_value, value=None
            )
        else:
            return Attribute.Constraint(
                type=constraint_type,
                from_=constraint_value,
                to_=constraint_value,
                value=constraint_value,
            )

    def _handle_unknown_type(self, attribute_type):
        """Handle unknown attribute type which are not present in bitmap, enum or struct list.

        :param attribute_type:
        :returns: The attribute type after processing.

        """
        logger.debug(f"Handling unknown attribute type {attribute_type}")
        if "bitmap" in attribute_type.lower():
            return "uint8"
        if "enum" in attribute_type.lower():
            return "uint8"
        if "struct" in attribute_type.lower():
            return "list"
        return attribute_type

    def _get_attribute_min_max_value(self, attr, attribute):
        """Get the min and max value of the attribute

        :param attr: The attribute object to process.
        :param attribute: The attribute element from the cluster XML file.
        """
        attr.min_value = None
        attr.max_value = None

        if "enum" in attr.type.lower():
            # For enums, check if it's in the data_types to get number of items
            attr_type = attribute.get("type", "").lower()
            if attr_type in self.cluster.data_types.get("enums", {}):
                enum_data = self.cluster.data_types.get("enums", {}).get(attr_type)
                if enum_data and hasattr(enum_data, "items"):
                    # Set bounds based on number of enum items
                    attr.min_value = "0"
                    attr.max_value = str(len(enum_data.items) - 1)
                    return
            else:
                logger.debug(f"Skipping - enum {attr_type} not found in data_types")
                return
        elif "bitmap" in attr.type.lower():
            # For bitmaps, check if it's in the data_types to get highest bit
            attr_type = attribute.get("type", "").lower()
            if attr_type in self.cluster.data_types.get("bitmaps", {}):
                bitmap_data = self.cluster.data_types.get("bitmaps", {}).get(attr_type)
                if bitmap_data and hasattr(bitmap_data, "bitfields"):
                    attr.min_value = "0"
                    attr.max_value = str(2 ** len(bitmap_data.bitfields) - 1)
                    return
            else:
                logger.debug(f"Skipping - bitmap {attr_type} not found in data_types")
                return
        else:
            constraint_elem = attribute.find("constraint")
            if constraint_elem:
                min_elem = constraint_elem.find("min")
                if min_elem is not None and min_elem.get("value") is not None:
                    attr.min_value = min_elem.get("value", "")
                max_elem = constraint_elem.find("max")
                if max_elem is not None and max_elem.get("value") is not None:
                    attr.max_value = max_elem.get("value", "")

                between_elem = constraint_elem.find("between")
                if between_elem is not None:
                    from_elem = between_elem.find("from")
                    to_elem = between_elem.find("to")
                    if from_elem is not None and from_elem.get("value") is not None:
                        attr.min_value = from_elem.get("value", "")
                    if to_elem is not None and to_elem.get("value") is not None:
                        attr.max_value = to_elem.get("value", "")

                length_between_elem = constraint_elem.find("lengthBetween")
                if length_between_elem is not None:
                    from_elem = length_between_elem.find("from")
                    to_elem = length_between_elem.find("to")
                    if from_elem is not None and from_elem.get("value") is not None:
                        attr.min_value = from_elem.get("value", "")
                    if to_elem is not None and to_elem.get("value") is not None:
                        attr.max_value = to_elem.get("value", "")

                max_length_elem = constraint_elem.find("maxLength")
                if (
                    max_length_elem is not None
                    and max_length_elem.get("value") is not None
                ):
                    attr.max_value = max_length_elem.get("value", "")
                    if attr.min_value is None:
                        attr.min_value = 0

        if (
            attr.min_value
            and isinstance(attr.min_value, str)
            and "0x" in attr.min_value
        ):
            attr.min_value = int(attr.min_value, 16)
        if (
            attr.max_value
            and isinstance(attr.max_value, str)
            and "0x" in attr.max_value
        ):
            attr.max_value = int(attr.max_value, 16)

        if (
            attr.min_value
            and isinstance(attr.min_value, str)
            and not attr.min_value.lstrip("-").isdigit()
        ):
            attr.min_value = None
        if (
            attr.max_value
            and isinstance(attr.max_value, str)
            and not attr.max_value.lstrip("-").isdigit()
        ):
            attr.max_value = None
        self._get_default_bounds_by_type(attr)
        if attr.min_value is not None:
            attr.min_value = int(attr.min_value)
        if attr.max_value is not None:
            attr.max_value = int(attr.max_value)

    def _get_default_bounds_by_type(self, attr):
        """Get the default bounds by type

        :param attr: The attribute object to process.
        """

        if attr.min_value is None:
            match attr.type:
                case "int8":
                    attr.min_value = -128
                case "int16" | "int32" | "int64":
                    attr.min_value = -32768
                case "uint8" | "uint16" | "uint32" | "uint64":
                    attr.min_value = 0

        if attr.max_value is None:
            match attr.type:
                case "int8":
                    attr.max_value = 126
                case "int16" | "int32" | "int64":
                    attr.max_value = 32766
                case "uint8":
                    attr.max_value = 254
                case "uint16" | "uint32" | "uint64":
                    attr.max_value = 65534

    def _update_attribute_type_by_default_value(self, attribute, attribute_type) -> str:
        """Update the attribute type by default value
        Sometimes attribute type for enum and bitmap is inferred from data type parser is incorrect so we need to update it by default value
        :param attribute: The attribute element from the cluster XML file.
        :param attribute_type: The attribute type.
        """
        default_value = attribute.get("default", "")
        try:
            if default_value is not None:
                if default_value.startswith("0x"):
                    default_value = int(default_value, 16)
                elif default_value.isdigit():
                    default_value = int(default_value)
                else:
                    default_value = None
        except ValueError:
            return attribute_type

        if default_value is not None:
            if default_value > 255 and attribute_type == "enum8":
                attribute_type = "enum16"
            elif default_value > 65535 and attribute_type == "enum16":
                attribute_type = "enum32"
            elif int(default_value) > 4294967295 and attribute_type == "enum32":
                attribute_type = "enum64"
            elif default_value > 255 and attribute_type == "bitmap8":
                attribute_type = "bitmap16"
            elif default_value > 65535 and attribute_type == "bitmap16":
                attribute_type = "bitmap32"
            elif default_value > 4294967295 and attribute_type == "bitmap32":
                attribute_type = "bitmap64"
        return attribute_type
