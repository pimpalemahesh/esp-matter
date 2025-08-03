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
import os
import logging
from utils.config import FileNames
from utils.helper import write_to_file, VERIFY_OR_EXIT
from chip_sources.cluster_mapping import normalize_cluster_name
from chip_sources.cluster_mapping import (
    generate_delegate_cluster_mapping,
    generated_plugin_init_cb_cluster_mapping,
)
from chip_sources.zap_filter import generate_zap_filter_list
from chip_sources.internally_managed_attributes import (
    get_internally_managed_attributes,
)

logger = logging.getLogger(__name__)


def generate_migrated_clusters(root_dir, migrated_clusters_json_file_path):
    """Find all clusters that have a CodegenIntegration.cpp file

    Args:
        root_dir: The root directory to search in
        migrated_clusters_json_file_path: Path to save the migrated clusters list
    Returns:
        True if successful, False otherwise
    """
    migrated_clusters = []

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if (
                filename.lower() == "codegenintegration.cpp"
                or filename.lower() == "codegeninstance.cpp"
            ):
                cluster_name = os.path.basename(dirpath)
                migrated_clusters.append(normalize_cluster_name(cluster_name))
            else:
                with open(os.path.join(dirpath, filename), "r") as file:
                    if "DefaultServerCluster" in file.read():
                        cluster_name = os.path.basename(dirpath)
                        migrated_clusters.append(normalize_cluster_name(cluster_name))

    migrated_clusters.sort()

    if write_to_file(migrated_clusters_json_file_path, migrated_clusters, "json"):
        return True
    return False


def generate_requirements(esp_matter_path, output_dir):
    """
    Generate all the required intermediate server files

    Args:
        esp_matter_path: Path to the ESP Matter repository
        output_dir: Directory where the generated files will be stored
    Returns:
        True if successful, False otherwise
    """
    os.makedirs(output_dir, exist_ok=True)

    chip_dir = os.path.join(esp_matter_path, "connectedhomeip/connectedhomeip")
    root_cluster_server_dir = os.path.join(chip_dir, "src/app/clusters/")
    header_files_dir = os.path.join(chip_dir, "zzz_generated/app-common/clusters")
    plugin_cb_header_file = os.path.join(
        esp_matter_path,
        "components/esp_matter/zap_common/app/PluginApplicationCallbacks.h",
    )

    VERIFY_OR_EXIT(
        os.path.exists(root_cluster_server_dir),
        f"Clusters directory {root_cluster_server_dir} does not exist",
    )

    VERIFY_OR_EXIT(
        os.path.exists(header_files_dir),
        f"Header files directory {header_files_dir} does not exist",
    )

    VERIFY_OR_EXIT(
        os.path.exists(plugin_cb_header_file),
        f"Plugin callback header file {plugin_cb_header_file} does not exist",
    )

    file_paths = {
        FileNames.INTERNALLY_MANAGED_ATTRIBUTES: os.path.join(
            output_dir, FileNames.INTERNALLY_MANAGED_ATTRIBUTES.value
        ),
        FileNames.DELEGATE_CLUSTERS: os.path.join(
            output_dir, FileNames.DELEGATE_CLUSTERS.value
        ),
        FileNames.PLUGIN_INIT_CB_CLUSTERS: os.path.join(
            output_dir, FileNames.PLUGIN_INIT_CB_CLUSTERS.value
        ),
        FileNames.ZAP_FILTER_LIST: os.path.join(output_dir, FileNames.ZAP_FILTER_LIST.value),
        FileNames.MIGRATED_CLUSTERS: os.path.join(
            output_dir, FileNames.MIGRATED_CLUSTERS.value
        ),
    }

    logger.debug(
        "Generating internally managed attributes from both server files and zcl.json..."
    )
    zcl_json_path = os.path.join(chip_dir, "src/app/zap-templates/zcl/zcl.json")
    VERIFY_OR_EXIT(
        os.path.exists(zcl_json_path), f"zcl.json file {zcl_json_path} does not exist"
    )
    is_generated = get_internally_managed_attributes(
        root_cluster_server_dir,
        zcl_json_path,
        file_paths[FileNames.INTERNALLY_MANAGED_ATTRIBUTES],
    )
    VERIFY_OR_EXIT(is_generated, "Failed to generate internally managed attributes")

    logger.debug("Generating delegate clusters...")
    is_generated = generate_delegate_cluster_mapping(
        root_cluster_server_dir, file_paths[FileNames.DELEGATE_CLUSTERS]
    )
    VERIFY_OR_EXIT(is_generated, "Failed to generate delegate clusters")

    logger.debug("Generating plugin init callback clusters...")
    is_generated = generated_plugin_init_cb_cluster_mapping(
        plugin_cb_header_file, file_paths[FileNames.PLUGIN_INIT_CB_CLUSTERS]
    )
    VERIFY_OR_EXIT(is_generated, "Failed to generate plugin init callback clusters")

    logger.debug("Generating include list...")
    is_generated = generate_zap_filter_list(
        header_files_dir, file_paths[FileNames.ZAP_FILTER_LIST]
    )
    VERIFY_OR_EXIT(is_generated, "Failed to generate include list")

    logger.debug("Finding migrated clusters...")
    is_generated = generate_migrated_clusters(
        root_cluster_server_dir, file_paths[FileNames.MIGRATED_CLUSTERS]
    )
    VERIFY_OR_EXIT(is_generated, "Failed to generate migrated clusters")

    return True
