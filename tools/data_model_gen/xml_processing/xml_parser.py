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
import click
import logging
import xml.etree.ElementTree as ET

from chip_sources import parser as chip_source_parser
from .cluster_parser import ClusterParser
from .device_parser import DeviceParser
from utils.helper import write_to_file, VERIFY_OR_EXIT
from utils.config import (
    FileNames,
    setup_logger,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_CHIP_VERSION,
)

logger = logging.getLogger(__name__)


def get_base_and_derived_cluster_files(input_dir):
    """Get all base and derived cluster files from the input directory."""
    base_cluster_files = []
    derived_cluster_files = []
    for file_name in os.listdir(input_dir):
        if file_name and file_name.endswith(".xml"):
            file_path = os.path.join(input_dir, file_name)
            tree = ET.parse(file_path)
            root = tree.getroot()
            classification = root.find("classification")
            if (
                classification is not None
                and classification.get("hierarchy", "") == "derived"
            ):
                derived_cluster_files.append(file_path)
            else:
                base_cluster_files.append(file_path)
        else:
            logger.warning(f"Skipping {file_name} as it is not a valid file")
            continue
    return base_cluster_files, derived_cluster_files


def process_cluster_files(
    input_dir,
    output_dir,
    yaml_file_path,
):
    """Process all cluster XML files from input directory and generate intermediate cluster json file.
    First it generates base cluster objects as during parsing of the derived cluster files, the base cluster objects are needed.
    Then it generates derived cluster objects.

    :param input_dir: Path to the directory containing the cluster XML files.
    :param output_dir: Path to the output directory.
    :returns: None

    """
    # Stores list of base and derived cluster XML files to be processed
    base_cluster_xml_files, derived_cluster_xml_files = (
        get_base_and_derived_cluster_files(input_dir)
    )
    if len(base_cluster_xml_files) == 0 and len(derived_cluster_xml_files) == 0:
        logger.error(f"No cluster XML files found in {input_dir}")
        return

    cluster_parser = ClusterParser()
    # Stores list of base and derived cluster objects
    base_clusters = []
    derived_clusters = []

    # Process base cluster files
    for file_path in base_cluster_xml_files:
        cluster_list = cluster_parser.parse(
            file_path=file_path,
            output_dir=output_dir,
            yaml_file_path=yaml_file_path,
        )

        if cluster_list is None or len(cluster_list) == 0:
            logger.error(
                f"********************** Processing of {os.path.basename(file_path)} failed************************"
            )
            continue

        base_clusters.extend(cluster_list)

    # Process derived cluster files
    for file_path in derived_cluster_xml_files:
        cluster_list = cluster_parser.parse(
            file_path=file_path,
            output_dir=output_dir,
            base_clusters=base_clusters,
            yaml_file_path=yaml_file_path,
        )

        if cluster_list is None or len(cluster_list) == 0:
            logger.error(
                f"********************** Processing of {os.path.basename(file_path)} failed************************"
            )
            continue

        derived_clusters.extend(cluster_list)

    clusters = base_clusters + derived_clusters
    # Convert clusters to list of dictionaries
    clusters_list = [cluster.to_dict() for cluster in clusters]
    clusters_list.sort(key=lambda x: int(x.get("id", "0"), 16))

    output_cluster_json_file = os.path.join(output_dir, FileNames.CLUSTER_JSON.value)
    if not write_to_file(output_cluster_json_file, clusters_list, "json"):
        logger.error(f"Failed to write to {output_cluster_json_file}")
        return

    logger.info(f"GENERATED cluster json at {output_dir}/clusters.json\n")


def parse_single_device_file(device_parser, file_path):
    """Parse a single device XML file and return the parsed device object.

    :param device_parser: Instance of DeviceParser.
    :param file_path: path to the device xml file
    :returns: Device object after parsing

    """
    return device_parser.parse_device_file(file_path)


def parse_single_cluster_file(
    cluster_parser, file_path, output_dir, yaml_file_path=None
):
    """Parse a single cluster XML file and return the parsed cluster object.

    :param cluster_parser: Instance of ClusterParser.
    :param file_path: Path to the cluster XML file.
    :param output_dir: Path to the output directory.
    :param yaml_file_path: Path to the config-data.yml file in connectedhomeip
    :returns: Cluster object after parsing

    """
    return cluster_parser.parse(file_path, output_dir, yaml_file_path=yaml_file_path)


def process_device_files(input_dir, output_dir):
    """Process all device XML files from input directory and generate intermediate device json file.

    :param input_dir: Path to the directory containing the device XML files.
    :param output_dir: Path to the output directory.
    :returns: None

    """
    devices = []
    device_parser = DeviceParser()
    for file_name in os.listdir(input_dir):
        if file_name and file_name.endswith(".xml"):
            file_path = os.path.join(input_dir, file_name)
            device = parse_single_device_file(
                device_parser=device_parser, file_path=file_path
            )
            if device is None or device.name is None:
                logger.error(
                    f"********************** Processing of {file_name} failed************************"
                )
                continue

            devices.append(device)
        else:
            logger.warning(f"Skipping {file_name} as it is not a valid file")
            continue

    devices_list = [device.to_dict() for device in devices]
    devices_list.sort(key=lambda x: int(x.get("id", "0"), 16))
    output_device_json_file = os.path.join(output_dir, FileNames.DEVICE_JSON.value)
    # Save devices to JSON
    if not write_to_file(output_device_json_file, devices_list, "json"):
        logger.error(f"Failed to write to {output_device_json_file}")
        return
    logger.info(f"GENERATED device json at {output_dir}/device_types.json\n")


def process_single_files(
    cluster_file,
    device_file,
    output_dir,
    yaml_file_path=None,
):
    """
    Process command line arguments for single file processing.

    :param args: Command line arguments
    :param output_dir: Path to the output directory.
    :param yaml_file_path: Path to the yaml configuration file.
    """
    if cluster_file is None and device_file is None:
        logger.error("Either cluster input file or device input file must be provided")
        return

    if cluster_file is not None:
        cluster_parser = ClusterParser()
        clusters = []
        cluster_list = cluster_parser.parse(
            file_path=cluster_file,
            output_dir=output_dir,
            yaml_file_path=yaml_file_path,
        )
        if cluster_list is not None:
            clusters.extend([cluster.to_dict() for cluster in cluster_list])
            output_cluster_json_file = os.path.join(
                output_dir, FileNames.CLUSTER_JSON.value
            )
            if not write_to_file(output_cluster_json_file, clusters, "json"):
                logger.error(f"Failed to write to {output_cluster_json_file}")
                return
            logger.info(f"GENERATED cluster json at {output_dir}/clusters.json\n")
        else:
            logger.error(f"Failed to parse cluster file {cluster_file}")
    if device_file is not None:
        device_parser = DeviceParser()
        devices = []
        device = device_parser.parse_device_file(file_path=device_file)
        if device is not None:
            devices.append(device.to_dict())
            output_device_json_file = os.path.join(
                output_dir, FileNames.DEVICE_JSON.value
            )
            if not write_to_file(output_device_json_file, devices, "json"):
                logger.error(f"Failed to write to {output_device_json_file}")
                return
            logger.info(f"GENERATED device json at {output_dir}/device_types.json\n")
        else:
            logger.error(f"Failed to parse device file {device_file}")


@click.command()
@click.option(
    "--cluster-file", type=str, help="Path to the input cluster xml file to process."
)
@click.option(
    "--device-file", type=str, help="Path to the input device xml file to process."
)
@click.option(
    "--cluster-dir",
    type=str,
    help="Path to the input cluster xml files directory to process.",
)
@click.option(
    "--device-dir",
    type=str,
    help="Path to the input device xml files directory to process.",
)
@click.option(
    "--chip-version",
    type=str,
    default=DEFAULT_CHIP_VERSION,
    help="XML's version to use.",
)
@click.option(
    "--output-dir",
    type=str,
    default=DEFAULT_OUTPUT_DIR,
    help="Path to the output directory.",
)
@click.option("--verbose", is_flag=True, help="Whether to use verbose output.")
@click.option("--no-colored-logs", is_flag=True, help="Whether to use colored output.")
def main(
    cluster_file,
    device_file,
    cluster_dir,
    device_dir,
    chip_version,
    output_dir,
    verbose,
    no_colored_logs,
):
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logger(log_level, not no_colored_logs)

    ESP_DIR = os.getenv("ESP_MATTER_PATH", None)
    VERIFY_OR_EXIT(ESP_DIR is not None, "ESP_MATTER_PATH is not set")
    CHIP_DIR = os.path.join(ESP_DIR, "connectedhomeip/connectedhomeip")

    # Yaml file contains list of clusters supporting specific functions e.g. Shutdown callback functions, pre attribute change callback functions, etc.
    yaml_file_path = os.path.join(
        CHIP_DIR,
        "src/app/common/templates/config-data.yaml",
    )
    VERIFY_OR_EXIT(os.path.exists(yaml_file_path), "Yaml file does not exist")
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    json_generated_dir = os.path.join(current_dir, output_dir)
    os.makedirs(json_generated_dir, exist_ok=True)
    root_cluster_server_dir = os.path.join(CHIP_DIR, "src/app/clusters/")
    VERIFY_OR_EXIT(
        os.path.exists(root_cluster_server_dir), "Clusters directory does not exist"
    )

    VERIFY_OR_EXIT(
        chip_source_parser.generate_requirements(
            esp_matter_path=ESP_DIR,
            output_dir=json_generated_dir,
        ),
        "Failed to generate intermediate files",
    )

    if cluster_file or device_file:
        # Process single file based on provided arguments
        process_single_files(
            cluster_file=cluster_file,
            device_file=device_file,
            yaml_file_path=yaml_file_path,
            output_dir=json_generated_dir,
        )
    else:
        if not cluster_dir and not device_dir:
            xml_input_dir = os.path.join(CHIP_DIR, f"data_model/{chip_version}/")
            VERIFY_OR_EXIT(
                os.path.exists(xml_input_dir),
                f"Data model directory for version {chip_version} does not exist",
            )
            cluster_input_dir = os.path.join(xml_input_dir, "clusters/")
            device_input_dir = os.path.join(xml_input_dir, "device_types/")
            VERIFY_OR_EXIT(
                os.path.exists(cluster_input_dir),
                f"Clusters directory for version {chip_version} does not exist",
            )
            VERIFY_OR_EXIT(
                os.path.exists(device_input_dir),
                f"Device types directory for version {chip_version} does not exist",
            )
        else:
            cluster_input_dir = cluster_dir
            device_input_dir = device_dir
            VERIFY_OR_EXIT(
                os.path.exists(cluster_input_dir),
                f"Clusters directory for version {chip_version} does not exist",
            )
            VERIFY_OR_EXIT(
                os.path.exists(device_input_dir),
                f"Device types directory for version {chip_version} does not exist",
            )

        logger.debug(
            "************************************************* Processing device files *************************************************"
        )
        process_device_files(
            input_dir=device_input_dir,
            output_dir=json_generated_dir,
        )

        logger.debug(
            "\n\n************************************************* Processing cluster files *************************************************"
        )
        process_cluster_files(
            input_dir=cluster_input_dir,
            output_dir=json_generated_dir,
            yaml_file_path=yaml_file_path,
        )


if __name__ == "__main__":
    main()
