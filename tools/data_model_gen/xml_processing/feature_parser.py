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
from .conformance_parser import (
    parse_conformance,
    match_conformance_items,
)
from .elements import Feature

logger = logging.getLogger(__name__)


class FeatureParser:

    def __init__(self, root, cluster):
        self.root = root
        self.cluster = cluster
        self.feature_map = {}
        self.processed_features = set()

    def create_feature_map(self):
        """Create a map of features from XML. e.g. {"LT": <lighting_feature_obj>}

        :param root: The root element of the cluster XML file.
        :returns: A map of features.

        """
        features_elem = self.root.find("features")
        if features_elem is None:
            logger.debug(f"No features found for cluster {self.cluster.name}")
            return self.feature_map

        feature_codes = self._collect_features()

        # create basic features without conformance as the conformance of features is dependent on the other features
        for feature_elem in features_elem.findall("feature"):
            feature = self._create_basic_feature(feature_elem, feature_codes)
            if feature:
                self.feature_map[feature.code] = feature

        # parse conformance now that all features exist in the feature map
        features_to_remove = []
        for feature_elem in features_elem.findall("feature"):
            feature_code = feature_elem.get("code")
            if feature_code and feature_code in self.feature_map:
                logger.debug(f"Parsing feature {feature_elem.get('name')}")
                should_remove = self._parse_feature_conformance(
                    feature_elem, self.feature_map[feature_code]
                )
                if should_remove:
                    features_to_remove.append(feature_code)

        # remove features with disallowed conformance
        for feature_code in features_to_remove:
            del self.feature_map[feature_code]

        return self.feature_map

    def _collect_features(self) -> list[str]:
        """Collect feature codes from XML. e.g. ["LT", "AC"]

        :returns: A list of feature codes.
        """
        features_elem = self.root.find("features")
        if features_elem is None:
            logger.debug(f"No features found for cluster {self.cluster.name}")
            return []
        features = []
        for feature_elem in features_elem.findall("feature"):
            feature_code = feature_elem.get("code")
            if feature_code:
                features.append(feature_code)
        return features

    def _create_basic_feature(self, feature_elem, feature_codes: list[str]):
        """Create a basic Feature object from XML element without conformance

        :param feature_elem:
        :param feature_codes: A list of all feature codes in the cluster.
        :returns: The created Feature object.

        """
        feature_name = feature_elem.get("name")
        if not feature_name:
            logger.debug(f"Skipping - missing feature name {feature_elem}")
            return None
        if feature_name in self.processed_features:
            logger.debug(f"Skipping - feature name already processed {feature_name}")
            return None
        self.processed_features.add(feature_name)
        feature_code = feature_elem.get("code")
        if not feature_code:
            logger.debug(f"Skipping - missing feature code {feature_elem}")
            return None
        feature_summary = feature_elem.get("summary")
        feature_bit = feature_elem.get("bit")

        feature_obj = Feature(
            name=(feature_name),
            code=feature_code,
            id=self._compute_feature_id(int(feature_bit)),
        )

        if feature_summary:
            feature_obj.summary = feature_summary

        return feature_obj

    def _parse_feature_conformance(self, feature_elem, feature_obj):
        """Parse and set conformance for a feature object

        :param feature_elem: XML element containing conformance information
        :param feature_obj: The Feature object to set conformance on
        :returns: True if feature should be removed (disallowed), False otherwise

        """
        first_child = next(iter(feature_elem), None)
        if first_child is None:
            return False

        if (
            first_child.tag == "provisionalConform"
            or first_child.tag == "deprecateConform"
            or first_child.tag == "disallowConform"
        ):
            logger.debug(f"Feature has {first_child.tag} conformance")
            return True

        feature_obj.conformance = parse_conformance(feature_elem, self.feature_map)

        if first_child.tag == "otherwiseConform":
            next_child = next(iter(first_child), None)
            if next_child is not None and (
                next_child.tag == "provisionalConform"
                or next_child.tag == "deprecateConform"
                or next_child.tag == "disallowConform"
            ):
                logger.debug(f"Feature has {next_child.tag} conformance")
                return True

        return False

    def _compute_feature_id(self, feature_bit):
        """Compute the feature id based on the number of existing features. e.g. feature_bit = 0x1, feature_id = 0x1 << 0x1 = 0x2, feature_bit = 0x2, feature_id = 0x1 << 0x2 = 0x4 etc.

        :param feature_bit:
        :returns: The computed feature id.

        """
        feature_id = 0x1 << feature_bit
        return feature_id

    def compute_features(self, feature_map, base_features: list[Feature] = None):
        """Add feature data to cluster

        :param feature_map: The feature map.
        :param base_features: list[Feature]:  (Default value = None)
        :returns: None

        """
        logger.debug("Collect features with dependent data model elements")
        for feature_obj in feature_map.values():
            self._process_feature(feature_obj, base_features)
            self.cluster.features.add(feature_obj)

        # Add base features to the cluster if they are not already in the cluster
        if base_features:
            for base_feature in base_features:
                if base_feature.code not in self.feature_map.keys():
                    self.cluster.features.add(base_feature)

    def _process_feature(self, feature_obj, base_features: list[Feature] = None):
        """This will create a list of attributes, commands and events those having conformance with the given feature.

        :param feature_obj: The feature object to process.
        :param base_features: list[Feature]:  (Default value = None)
        :returns: None

        """
        # Match attributes to features
        feature_attribute_list = match_conformance_items(
            feature_obj, self.cluster.get_attribute_list()
        )
        if feature_attribute_list:
            feature_obj.add_attribute_list(feature_attribute_list)

        # Match commands to features
        feature_command_list = match_conformance_items(
            feature_obj, self.cluster.get_command_list()
        )

        if feature_command_list:
            feature_obj.add_command_list(feature_command_list)

        # Match events to features
        feature_event_list = match_conformance_items(
            feature_obj, self.cluster.get_event_list()
        )
        if feature_event_list:
            feature_obj.add_event_list(feature_event_list)
