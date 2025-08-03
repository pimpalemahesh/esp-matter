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
import click
from jinja2 import Environment, FileSystemLoader
from .deserializer import ClusterDeserializer, DeviceDeserializer
from .elements import Cluster, Device
from typing import List

from utils.config import (
    setup_logger,
    DEFAULT_DATA_MODEL_DIR,
)
from utils.helper import write_to_file, VERIFY_OR_EXIT

template_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "templates"
)


def format_filter(value, fmt):
    """Format filter for Jinja templates"""
    return fmt.format(value)


env = Environment(
    loader=FileSystemLoader(template_dir),
    trim_blocks=True,
    lstrip_blocks=True,
    extensions=["jinja2.ext.do"],
)
env.filters["format_filter"] = format_filter


def get_template(template_name):
    """Get a Jinja template by name"""
    template = env.get_template(template_name)
    VERIFY_OR_EXIT(template is not None, f"Template {template_name} not found")
    return template


CLUSTER_CPP_TEMPLATE = "cluster.cpp.jinja"
CLUSTER_H_TEMPLATE = "cluster.h.jinja"
CLUSTER_IDS_TEMPLATE = "cluster_ids.h.jinja"
DEVICE_CPP_TEMPLATE = "device.cpp.jinja"
DEVICE_H_TEMPLATE = "device.h.jinja"

logger = logging.getLogger(__name__)


def get_all_cluster_objects(json_path: str) -> List[Cluster]:
    """Parse JSON file and create Cluster objects

    :param json_path: The path to the JSON file
    :returns: A list of clusters
    """
    return ClusterDeserializer().derserialize(json_path)


def get_all_device_objects(json_path: str, clusters: List[Cluster]) -> List[Device]:
    """Parse device types JSON and create Device objects

    :param json_path: The path to the JSON file
    :param clusters: A list of clusters
    :returns: A list of devices
    """
    cluster_lookup_table = {cluster.esp_name: cluster for cluster in clusters}
    return DeviceDeserializer().derserialize(json_path, cluster_lookup_table)


def render_templates(object, cpp_template_obj, h_template_obj):
    """Renders the C++ and header templates for the cluster or device.

    :param object: The cluster or device object to render the templates for.
    :param cpp_template_obj: The C++ template object.
    :param h_template_obj: The header template object.
    :returns: A tuple containing the rendered C++ and header code.

    """
    try:
        if isinstance(object, Cluster):
            cpp_code = cpp_template_obj.render(cluster=object)
            h_code = h_template_obj.render(cluster=object)
            return cpp_code, h_code
        elif isinstance(object, Device):
            cpp_code = cpp_template_obj.render(device=object)
            h_code = h_template_obj.render(device=object)
            return cpp_code, h_code
    except Exception as e:
        raise Exception(f"Error rendering templates for {object.name}: {str(e)}") from e


def save_generated_files(file_name, cpp_code, h_code, output_dir):
    """Saves the generated C++ and header files.

    :param file_name: The name of the file to save.
    :param cpp_code: The rendered C++ code.
    :param h_code: The rendered header code.
    :param output_dir: The directory to save the generated files.

    """
    try:
        cpp_file_path = os.path.join(output_dir, f"{file_name}.cpp")
        h_file_path = os.path.join(output_dir, f"{file_name}.h")
        write_to_file(cpp_file_path, cpp_code)
        write_to_file(h_file_path, h_code)
    except FileNotFoundError as e:
        raise Exception(f"File not found: {e}") from e
    except Exception as e:
        raise Exception(
            f"Error saving generated files for cluster {file_name}: {str(e)}"
        ) from e


def generate_cluster_files(json_path, output_dir):
    """Parse cluster JSON and generate C++ and header files.

    :param json_path: The path to the cluster JSON file.
    :param output_dir: The directory to save the generated files.
    :returns: A list of clusters.

    """
    cluster_output_dir = os.path.join(output_dir, "clusters")
    cluster_name_list = []
    try:
        os.makedirs(cluster_output_dir, exist_ok=True)

        cpp_template = get_template(CLUSTER_CPP_TEMPLATE)
        h_template = get_template(CLUSTER_H_TEMPLATE)
        ids_template = get_template(CLUSTER_IDS_TEMPLATE)

        clusters = get_all_cluster_objects(json_path)

        for cluster in clusters:
            cpp_code, h_code = render_templates(cluster, cpp_template, h_template)
            ids_code = ids_template.render(cluster=cluster)
            cluster_specific_dir = os.path.join(cluster_output_dir, cluster.esp_name)
            os.makedirs(cluster_specific_dir, exist_ok=True)
            if cpp_code and h_code:
                save_generated_files(
                    cluster.esp_name,
                    cpp_code,
                    h_code,
                    cluster_specific_dir,
                )
                cluster_name_list.append(cluster.esp_name)
                ids_file_path = os.path.join(
                    cluster_specific_dir, f"{cluster.esp_name}_ids.h"
                )
                write_to_file(ids_file_path, ids_code)
        header_file_path = os.path.join(output_dir, "clusters", "all_cluster.h")
        generate_header_file(header_file_path, cluster_name_list)
        logger.info(
            f"********* Cluster Files Generated at: {cluster_output_dir} *********"
        )
        return clusters
    except Exception as e:
        raise Exception(f"Error parsing cluster JSON: {str(e)}") from e


def generate_device_files(json_path, output_dir, clusters: List[Cluster]):
    """Parse device JSON and generate C++ and header files.

    :param json_path: The path to the device JSON file.
    :param output_dir: The directory to save the generated files.
    :param clusters: A list of clusters.
    :returns: A list of devices.

    """
    device_output_dir = os.path.join(output_dir, "device_types")
    device_name_list = []

    try:
        os.makedirs(device_output_dir, exist_ok=True)

        cpp_template = get_template(DEVICE_CPP_TEMPLATE)
        h_template = get_template(DEVICE_H_TEMPLATE)
        devices = get_all_device_objects(json_path, clusters)
        for device in devices:
            cpp_code, h_code = render_templates(device, cpp_template, h_template)
            device_specific_dir = os.path.join(device_output_dir, device.filename)
            os.makedirs(device_specific_dir, exist_ok=True)
            if cpp_code and h_code:
                save_generated_files(
                    device.filename,
                    cpp_code,
                    h_code,
                    device_specific_dir,
                )
                device_name_list.append(device.filename)

        header_file_path = os.path.join(output_dir, "device_types", "all_device_type.h")
        generate_header_file(header_file_path, device_name_list)
        logger.info(
            f"********* Device Files Generated at: {device_output_dir} *********"
        )
        return devices
    except Exception as e:
        raise Exception(f"Error parsing device JSON: {str(e)}") from e


def generate_header_file(output_file_path: str, objects: List[str]):
    """Generate a all cluster and device header files.
    :param output_file_path: The filepath to save the header file.
    :param objects: A list of cluster or device names.
    """

    VERIFY_OR_EXIT(len(objects) > 0, "List of cluster or device names is empty")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    header_content = ["\n// This is a generated file. Do not edit this file.\n"]
    sorted_objects = sorted(objects)

    for object_name in sorted_objects:
        header_content.append(f'#include "{object_name}.h"\n')

    with open(output_file_path, "w") as f:
        f.writelines(header_content)
    logger.info(f"Generated header file: {output_file_path}")


@click.command()
@click.option(
    "--output-dir",
    type=str,
    default=DEFAULT_DATA_MODEL_DIR,
    help="Output directory to save the generated files.",
)
@click.option(
    "--cluster-json-path",
    type=str,
    required=True,
    help="Path to the cluster JSON file to process.",
)
@click.option(
    "--device-json-path",
    type=str,
    required=True,
    help="Path to the device JSON file to process.",
)
@click.option("--verbose", is_flag=True, help="Whether to use verbose output.")
@click.option("--no-colored-logs", is_flag=True, help="Whether to use colored logs.")
def main(output_dir, cluster_json_path, device_json_path, verbose, no_colored_logs):
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logger(log_level, not no_colored_logs)

    ESP_DIR = os.getenv("ESP_MATTER_PATH", None)
    VERIFY_OR_EXIT(ESP_DIR is not None, "ESP_MATTER_PATH is not set")
    VERIFY_OR_EXIT(
        os.path.exists(cluster_json_path),
        f"Cluster JSON file not found: {cluster_json_path}",
    )
    VERIFY_OR_EXIT(
        os.path.exists(device_json_path),
        f"Device JSON file not found: {device_json_path}",
    )
    os.makedirs(output_dir, exist_ok=True)

    try:
        clusters = generate_cluster_files(cluster_json_path, output_dir)
        generate_device_files(device_json_path, output_dir, clusters)
    except Exception as e:
        raise Exception(f"Error processing clusters or devices: {str(e)}") from e


if __name__ == "__main__":
    main()
