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
import json
import os
import logging
import xml.etree.ElementTree as ET

from .attribute_parser import AttributeParser
from .command_parser import CommandParser
from .data_type_parser import DataTypeParser
from .event_parser import EventParser
from .feature_parser import FeatureParser
from .yaml_parser import YamlParser
from .elements import Cluster
from utils.helper import check_valid_id, esp_name, hex_to_int, safe_get_attr
from utils.config import FileNames
from utils.exceptions import should_skip_cluster_command_callbacks

logger = logging.getLogger(__name__)
DUMMY_CLUSTER_ID = hex(0xFFFF)


class ClusterParser:
    """Class for parsing cluster data"""

    def parse(
        self,
        file_path,
        output_dir: str,
        yaml_file_path: str,
        base_clusters: list[Cluster] = None,
    ):
        """Parses an XML cluster file
        (A single base cluster file can have multiple derived clusters in single file)

        :param file_path: The path to the cluster XML file.
        :param output_dir: The path to the output directory.
        :param yaml_file_path: The path to the YAML file.
        :param base_clusters: list[Cluster]:  (Default value = None)
        :returns: A list of clusters.

        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        clusters = []
        # if single file has multiple cluster ids, then skip command callback generation for the cluster e.g. ResourceMonitoring
        skip_command_cb = False

        cluster_name_id_list = self._get_cluster_name_and_id(root)
        if not cluster_name_id_list or len(cluster_name_id_list) == 0:
            logger.warning(f"Skipping {file_path} as it is not a valid cluster")
            return clusters
        cluster_revision = root.get("revision", "1")
        if len(cluster_name_id_list) > 1:
            skip_command_cb = True

        for cluster_name, cluster_id in cluster_name_id_list:
            if not cluster_name or not cluster_id:
                logger.warning(
                    f"Skipping {file_path} as name or id is missing, (Either base cluster or not supported yet)"
                )
                continue
            if not check_valid_id(cluster_id):
                logger.warning(f"Skipping {file_path} as id is not valid: {cluster_id}")
                continue
            logger.debug(f"Parsing cluster {cluster_name} with id {cluster_id}")
            if base_clusters:
                base_cluster = self._get_base_cluster(root, base_clusters)
            else:
                base_cluster = None
            cluster = self._parse_cluster(
                root,
                cluster_name,
                cluster_id,
                cluster_revision,
                output_dir,
                yaml_file_path,
                base_cluster,
                skip_command_cb,
            )
            clusters.append(cluster)
        return clusters

    def _inherit_from_base_cluster(self, derived_cluster, base_cluster):
        """Inherit properties from base cluster to derived cluster
        This function will be used to inherit properties from base cluster to derived cluster when base cluster and derivied cluster files are separate.

        :param derived_cluster: The derived cluster.
        :param base_cluster: The base cluster.

        """
        if base_cluster.delegate_init_callback_available:
            derived_cluster.delegate_init_callback_available = True
        if base_cluster.attribute_changed_function_available:
            derived_cluster.attribute_changed_function_available = True
        if base_cluster.shutdown_function_available:
            derived_cluster.shutdown_function_available = True
        if base_cluster.pre_attribute_change_function_available:
            derived_cluster.pre_attribute_change_function_available = True
        if base_cluster.plugin_init_cb_available:
            derived_cluster.plugin_init_cb_available = True

    def _parse_cluster(
        self,
        root,
        cluster_name,
        cluster_id,
        cluster_revision,
        output_dir,
        yaml_file_path: str,
        base_cluster: Cluster = None,
        skip_command_cb: bool = False,
    ):
        """Parse a cluster from XML

        :param root: The root element of the cluster XML file.
        :param cluster_name: The name of the cluster.
        :param cluster_id: The ID of the cluster.
        :param cluster_revision: The revision of the cluster.
        :param output_dir: The path to the output directory.
        :param yaml_file_path: The path to the YAML file.
        :param base_cluster: Cluster:  (Default value = None)
        :param skip_command_cb: bool: Whether to skip command callback generation for the cluster.
        :returns: The parsed cluster.

        """
        cluster = Cluster(id=cluster_id, name=cluster_name, revision=cluster_revision)

        cluster.skip_command_cb = skip_command_cb
        if should_skip_cluster_command_callbacks(cluster.esp_name) or skip_command_cb:
            cluster.skip_command_cb = True
        allowed_attributes_ids = []
        allowed_commands_ids = []
        allowed_events_ids = []

        delegate_clusters_list = json.load(
            open(os.path.join(output_dir, FileNames.DELEGATE_CLUSTERS.value))
        )
        if cluster.esp_name in delegate_clusters_list:
            cluster.delegate_init_callback_available = True

        plugin_init_cb_clusters_list = json.load(
            open(os.path.join(output_dir, FileNames.PLUGIN_INIT_CB_CLUSTERS.value))
        )
        if cluster.esp_name in plugin_init_cb_clusters_list:
            cluster.plugin_init_cb_available = True

        migrated_clusters_list = json.load(
            open(os.path.join(output_dir, FileNames.MIGRATED_CLUSTERS.value))
        )
        if cluster.esp_name in migrated_clusters_list:
            cluster.is_migrated_cluster = True

        # Get filtered attributes, commands and events as only those are implemented/supported in the SDK
        zap_filter_list = json.load(
            open(os.path.join(output_dir, FileNames.ZAP_FILTER_LIST.value))
        )
        cluster_info = zap_filter_list.get("clusters", {}).get(cluster_id, {})
        if cluster_info:
            allowed_attributes_ids = hex_to_int(
                list(cluster_info.get("Attributes", {}).values())
            )
            allowed_commands_ids = hex_to_int(
                list(cluster_info.get("Commands", {}).values())
            )
            allowed_events_ids = hex_to_int(
                list(cluster_info.get("Events", {}).values())
            )

        if base_cluster:
            logger.debug(f"Inheriting metadata from base cluster {base_cluster.name}")
            self._inherit_from_base_cluster(cluster, base_cluster)

        classification = root.find("classification")
        if classification is not None:
            cluster.role = classification.get("role", "application")
            cluster.hierarchy = classification.get("hierarchy")
            base_cluster_name = classification.get("baseCluster")
            if base_cluster_name:
                cluster.base_cluster_name = esp_name(base_cluster_name)
            cluster.pics_code = classification.get("picsCode")
            cluster.scope = classification.get("scope")
        else:
            logger.debug(
                f"Classification element not found for cluster {cluster_name}, using default role 'application'"
            )
            cluster.role = "application"

        self._process_cluster_yaml(cluster, yaml_file_path)

        self._parse_revision_history(cluster, root)

        data_type_parser = DataTypeParser()
        feature_parser = FeatureParser(root, cluster)
        feature_map = feature_parser.create_feature_map()
        feature_parser.feature_map = feature_map

        managed_attributes = json.load(
            open(
                os.path.join(output_dir, FileNames.INTERNALLY_MANAGED_ATTRIBUTES.value)
            )
        ).get(safe_get_attr(cluster, "esp_name", ""), [])

        attribute_parser = AttributeParser(
            cluster,
            feature_parser.feature_map,
            managed_attributes,
            allowed_attributes_ids,
        )
        command_parser = CommandParser(
            cluster, feature_parser.feature_map, allowed_commands_ids
        )
        event_parser = EventParser(
            cluster, feature_parser.feature_map, allowed_events_ids
        )

        cluster.attribute_types = data_type_parser.parse(root)
        cluster.data_types = data_type_parser.get_data_types()

        base_attributes = base_cluster.attributes if base_cluster else []
        base_commands = base_cluster.commands if base_cluster else []
        base_events = base_cluster.events if base_cluster else []
        base_features = base_cluster.features if base_cluster else []
        attribute_parser.parse(root, base_attributes)
        command_parser.parse(root, base_commands)
        event_parser.parse(root, base_events)
        feature_parser.compute_features(feature_parser.feature_map, base_features)

        total_attributes = len(cluster.attributes)
        total_commands = len(cluster.commands)
        total_events = len(cluster.events)
        total_features = len(cluster.features)
        logger.debug(f"Processed cluster {cluster.name} successfully with {total_attributes} attributes, {total_commands} commands, {total_events} events and {total_features} features")
        return cluster

    def _parse_revision_history(self, cluster, root):
        """Parse revision history from XML

        :param cluster: The cluster to parse the revision history for.
        :param root: The root element of the cluster XML file.

        """
        revision_history_elem = root.find("revisionHistory")
        if revision_history_elem is not None:
            for revision in revision_history_elem.findall("revision"):
                revision_info = {
                    "revision": revision.get("revision", "1"),
                    "summary": revision.get("summary", ""),
                }
                cluster.revision_history.append(revision_info)

    def _get_cluster_name_and_id(self, root):
        """Get cluster name and id from XML

        :param root:
        :returns: A list of cluster name and id.

        """
        name_id_list = []
        cluster_name = root.get("name", "").replace(" Cluster", "")
        cluster_id = root.get("id")

        name_id_list.append([cluster_name, cluster_id])
        if cluster_name and cluster_id:
            return name_id_list

        if not cluster_name or not cluster_id:
            cluster_ids_element = root.find("clusterIds").findall("clusterId")
            for cluster_id_element in cluster_ids_element:
                cluster_name = cluster_id_element.get("name")
                cluster_id = cluster_id_element.get("id")
                if not cluster_id:
                    # Default to 0xFFFF if id is not present
                    cluster_id = hex(0xFFFF)
                if cluster_name and cluster_id:
                    name_id_list.append([cluster_name, cluster_id])

        return name_id_list

    def _get_base_cluster(self, root, base_clusters: list[Cluster]):
        """Get base cluster from root

        :param root: The root element of the cluster XML file.
        :param base_clusters: The base cluster list.
        :param base_clusters: list[Cluster]:

        """
        base_cluster = None
        base_cluster_name = root.find("classification").get("baseCluster")
        if base_cluster_name:
            base_cluster = next(
                (
                    bc
                    for bc in base_clusters
                    if esp_name(bc.name) == esp_name(base_cluster_name)
                ),
                None,
            )
        return base_cluster

    def _process_cluster_yaml(self, cluster, yaml_file_path: str):
        """Process cluster YAML file

        :param cluster: The cluster to process the YAML file for.
        :param yaml_file_path: The path to the YAML file.
        :param yaml_file_path: str:

        """
        if yaml_file_path:
            yaml_parser = YamlParser(yaml_file_path)
            if yaml_parser.is_present_in_list(
                "CommandHandlerInterfaceOnlyClusters", safe_get_attr(cluster, "name")
            ):
                cluster.command_handler_available = True
            if yaml_parser.is_present_in_list(
                "ClustersWithInitFunctions", safe_get_attr(cluster, "name")
            ):
                cluster.init_function_available = True
            if yaml_parser.is_present_in_list(
                "ClustersWithAttributeChangedFunctions", safe_get_attr(cluster, "name")
            ):
                cluster.attribute_changed_function_available = True
            if yaml_parser.is_present_in_list(
                "ClustersWithShutdownFunctions", safe_get_attr(cluster, "name")
            ):
                cluster.shutdown_function_available = True
            if yaml_parser.is_present_in_list(
                "ClustersWithPreAttributeChangeFunctions",
                safe_get_attr(cluster, "name"),
            ):
                cluster.pre_attribute_change_function_available = True
            if yaml_parser.is_present_in_list(
                "CodeDrivenClusters", safe_get_attr(cluster, "name")
            ):
                cluster.is_migrated_cluster = True
        else:
            logger.error(
                f"Yaml file not found for cluster: {safe_get_attr(cluster, 'name')}"
            )
