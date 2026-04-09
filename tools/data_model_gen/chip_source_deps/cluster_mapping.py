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
import os
import re

from utils.helper import convert_to_snake_case, write_to_file
from utils.helper import esp_name
from chip_source_deps.server_files_config import (
    local_mappings,
    parser,
    PLUGIN_CB_PATTERN,
    DELEGATE_METHODS,
    DELEGATE_VARIABLE_NAMES,
)

logger = logging.getLogger(__name__)


def normalize_cluster_name(cluster_name, type="file"):
    """Normalize a cluster name from a filename or a string

    :param cluster_name: The cluster name to normalize.
    :param type: The type of the cluster name.
    :returns: Normalized cluster name

    """
    if type == "file":
        cluster_name = os.path.basename(cluster_name).split(".")[0]
        cluster_name = cluster_name.replace("-server", "").lower()
        cluster_name = esp_name(cluster_name)
        cluster_name = local_mappings.get(cluster_name, cluster_name)
        return cluster_name

    cluster_name = convert_to_snake_case(cluster_name)
    cluster_name = local_mappings.get(cluster_name, cluster_name)
    cluster_name = cluster_name.replace(" ", "_")
    cluster_name = esp_name(cluster_name)

    return cluster_name


def check_if_delegate_method_available(node, code_bytes):
    """Check if delegate is available in the given file using tree-sitter.

    :param node: The AST node to search from
    :param code_bytes: The source code as bytes
    :returns: True if delegate method is available, False otherwise.
    """
    if node.type == "function_declarator" or node.type == "declaration":
        text = code_bytes[node.start_byte : node.end_byte].decode(
            "utf8", errors="ignore"
        )
        if any(method in text for method in DELEGATE_METHODS):
            return True
    if node.type == "class_specifier":
        for child in node.children:
            if child.type == "field_declaration_list":
                for field_declaration in child.children:
                    text = code_bytes[
                        field_declaration.start_byte : field_declaration.end_byte
                    ].decode("utf8", errors="ignore")
                    if any(method in text for method in DELEGATE_METHODS):
                        return True
                    if any(variable in text for variable in DELEGATE_VARIABLE_NAMES):
                        return True
    for child in node.children:
        if check_if_delegate_method_available(child, code_bytes):
            return True
    return False


def find_delegate_server_files(root_dir):
    """Find all delegate files in the given directory using tree-sitter.

    :param root_dir:
    :returns: cluster list with delegate.
    :rtype: Two sets

    """
    delegate_server_files = set()

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)

            # Check for delegate callback in server files
            if "-delegate.h" in filename.lower():
                cluster_name = normalize_cluster_name(dirpath, type="file")
                delegate_server_files.add(cluster_name)
            elif filename and filename.endswith(".h"):
                with open(full_path, "r") as f:
                    content = f.read()
                    tree = parser.parse(bytes(content, "utf8"))
                    root = tree.root_node
                    code_bytes = bytes(content, "utf8")
                    if check_if_delegate_method_available(root, code_bytes):
                        cluster_name = normalize_cluster_name(dirpath, type="file")
                        delegate_server_files.add(cluster_name)

    return sorted(list(delegate_server_files))


def generate_delegate_cluster_mapping(
    root_dir, delegate_cluster_json_file_path
) -> tuple[bool, str]:
    """Generate cluster mapping list for clusters with delegate

    :param root_dir: The root directory to search for server files.
    :param delegate_cluster_json_file_path: The path to the JSON file for delegate clusters.
    :returns: True if successful, False otherwise.
    """
    try:
        delegate_server_files = find_delegate_server_files(root_dir)
        if write_to_file(
            delegate_cluster_json_file_path, delegate_server_files, "json"
        ):
            logger.info(
                f"Successfully written Delegate Clusters to {delegate_cluster_json_file_path}"
            )
            return True, None
        return False, f"Error writing to {delegate_cluster_json_file_path}"
    except Exception as e:
        return False, f"Error generating delegate cluster mapping: {str(e)}"


def find_plugin_init_callbacks(node, code_bytes):
    """Find all MatterXXXPluginServerInitCallback function declarations using tree-sitter.

    :param node: The AST node to search from
    :param code_bytes: The source code as bytes
    :returns: List of cluster names
    """
    clusters = []

    if node.type == "function_declarator" or node.type == "declaration":
        text = code_bytes[node.start_byte : node.end_byte].decode(
            "utf8", errors="ignore"
        )

        pattern = re.compile(PLUGIN_CB_PATTERN)
        match = pattern.search(text)
        if match:
            cluster_name = match.group(1)
            snake_case = normalize_cluster_name(cluster_name, type="string")
            clusters.append(snake_case)

    for child in node.children:
        clusters.extend(find_plugin_init_callbacks(child, code_bytes))

    return clusters


def extract_cluster_names(header_file_path):
    """Extract cluster names from plugin init callback functions using tree-sitter.

    :param header_file_path: Path to the header file
    :returns: List of cluster names
    """
    try:
        with open(header_file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading file {header_file_path}: {e}")
        return []

    tree = parser.parse(bytes(content, "utf8"))
    root = tree.root_node
    code_bytes = bytes(content, "utf8")

    return find_plugin_init_callbacks(root, code_bytes)


def generated_plugin_init_cb_cluster_mapping(
    header_file_path, plugin_init_cb_cluster_json_file_path
) -> tuple[bool, str]:
    """
    Generate plugin init callback cluster mapping

    :param header_file_path: The path to the header file.
    :param plugin_init_cb_cluster_json_file_path: The path to the JSON file for plugin init callback clusters.
    :returns: True if successful, False otherwise.

    """
    try:
        if not os.path.isfile(header_file_path):
            logger.warning(f"File {header_file_path} does not exist")
            return False, f"File {header_file_path} does not exist"

        cluster_names = extract_cluster_names(header_file_path)
        if write_to_file(plugin_init_cb_cluster_json_file_path, cluster_names, "json"):
            logger.info(
                f"Successfully written Plugin Init Callback Clusters to {plugin_init_cb_cluster_json_file_path}"
            )
            return True, None
        return False, f"Error writing to {plugin_init_cb_cluster_json_file_path}"
    except Exception as e:
        return False, f"Error generating plugin init callback cluster mapping: {str(e)}"
