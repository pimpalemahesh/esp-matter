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
import os
import shutil
import click
from dataclasses import dataclass
from typing import Optional

from chip_sources import parser as chip_source_parser
from code_generation.code_generator import generate_cluster_files, generate_device_files
from xml_processing.xml_parser import (
    process_single_files,
    process_cluster_files,
    process_device_files,
)

from utils.config import (
    FileNames,
    DEFAULT_CHIP_VERSION,
    SPECIFICATION_VERSIONS,
    DEFAULT_DATA_MODEL_DIR,
    DEFAULT_OUTPUT_DIR,
    setup_logger,
)
from utils.helper import VERIFY_OR_EXIT

logger = logging.getLogger(__name__)


@dataclass
class DataModelGenConfig:
    """Configuration required to execute the data model generation pipeline."""

    esp_matter_path: str
    output_dir: str
    json_output_dir: str
    chip_version: str
    cluster_dir: Optional[str] = None
    device_dir: Optional[str] = None
    cluster_file: Optional[str] = None
    device_file: Optional[str] = None
    skip_xml_parsing: bool = False
    skip_code_generation: bool = False
    clean_output: bool = False


class DataModelGenerator:

    def __init__(self, config: DataModelGenConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.chip_dir = os.path.join(
            self.config.esp_matter_path, "connectedhomeip", "connectedhomeip"
        )
        self.yaml_file_path = self.get_yaml_file_path()

    def run(self) -> None:
        """Execute the data model generation pipeline."""
        self._prepare_output_directories()

        if not self.config.skip_xml_parsing:
            self.logger.info("Step 1: Parsing XML files to generate JSON intermediates")
            self._generate_intermediate_artifacts()
        else:
            self.logger.info("Skipping XML parsing as requested")

        if not self.config.skip_code_generation:
            self.logger.info("Step 2: Generating code from JSON intermediates")
            self._generate_code()
        else:
            self.logger.info("Skipping code generation as requested")

        self.logger.info(
            "Data model generation completed successfully. Output directory: %s",
            self.config.output_dir,
        )

    def _prepare_output_directories(self) -> None:
        """Ensure output directories exist and clean generated artifacts if requested."""
        if self.config.clean_output:
            self.logger.info(
                "Cleaning generated artifacts in %s", self.config.output_dir
            )
            for folder in ("clusters", "device_types"):
                target = os.path.join(self.config.output_dir, folder)
                if os.path.isdir(target):
                    shutil.rmtree(target)
            shutil.rmtree(self.config.json_output_dir)
        os.makedirs(self.config.json_output_dir, exist_ok=True)
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.config.output_dir, "clusters"), exist_ok=True)
        os.makedirs(os.path.join(self.config.output_dir, "device_types"), exist_ok=True)

    def _generate_intermediate_artifacts(self) -> None:
        """Create JSON intermediates from connectedhomeip sdk and XML definitions."""
        self._generate_chip_source_metadata()

        if self.config.cluster_file or self.config.device_file:
            process_single_files(
                cluster_file=self.config.cluster_file,
                device_file=self.config.device_file,
                output_dir=self.config.json_output_dir,
                yaml_file_path=self.yaml_file_path,
            )
        else:
            self.logger.debug(
                "Processing device XML files from %s", self.config.device_dir
            )
            process_device_files(
                input_dir=self.config.device_dir,
                output_dir=self.config.json_output_dir,
            )
            self.logger.debug(
                "Processing cluster XML files from %s", self.config.cluster_dir
            )
            process_cluster_files(
                input_dir=self.config.cluster_dir,
                output_dir=self.config.json_output_dir,
                yaml_file_path=self.yaml_file_path,
            )

    def _generate_chip_source_metadata(self) -> None:
        """Generate the required intermediate JSON files from the connectedhomeip sdk."""
        self.logger.debug("Generating CHIP server metadata artifacts")
        VERIFY_OR_EXIT(
            chip_source_parser.generate_requirements(
                esp_matter_path=self.config.esp_matter_path,
                output_dir=self.config.json_output_dir,
            ),
            "Failed to generate intermediate files from CHIP sources",
        )

    def _generate_code(self) -> None:
        """Generate the C++ data model files from the generated JSON artifacts."""
        cluster_json = os.path.join(
            self.config.json_output_dir, FileNames.CLUSTER_JSON.value
        )
        device_json = os.path.join(
            self.config.json_output_dir, FileNames.DEVICE_JSON.value
        )

        if os.path.exists(cluster_json):
            clusters = generate_cluster_files(cluster_json, self.config.output_dir)
            self.logger.debug(
                "Successfully generated cluster files for %d clusters", len(clusters)
            )
        else:
            self.logger.warning(
                "Cluster JSON file not found at %s (skipping cluster generation)",
                cluster_json,
            )
            clusters = []

        if os.path.exists(device_json):
            devices = generate_device_files(
                device_json, self.config.output_dir, clusters
            )
            self.logger.debug(
                "Successfully generated device files for %d devices", len(devices)
            )
        else:
            self.logger.warning(
                "Device JSON file not found at %s (skipping device generation)",
                device_json,
            )
            devices = []

    def get_yaml_file_path(self) -> str:
        """Get the path to the CHIP YAML configuration file."""
        file_path = os.path.join(
            self.chip_dir, "src", "app", "common", "templates", "config-data.yaml"
        )
        VERIFY_OR_EXIT(
            os.path.exists(file_path),
            f"YAML configuration file does not exist: {file_path}",
        )
        return file_path


@click.command()
@click.option(
    "--output-dir",
    default=DEFAULT_DATA_MODEL_DIR,
    help=f"Directory where generated files will be written (default: {DEFAULT_DATA_MODEL_DIR})",
)
@click.option(
    "--cluster-file", type=str, help="Path to a specific cluster XML file to process"
)
@click.option(
    "--device-file", type=str, help="Path to a specific device XML file to process"
)
@click.option(
    "--cluster-dir",
    type=str,
    help="Path to a directory that contains cluster XML files",
)
@click.option(
    "--device-dir", type=str, help="Path to a directory that contains device XML files"
)
@click.option(
    "--chip-version",
    default=DEFAULT_CHIP_VERSION,
    type=click.Choice(SPECIFICATION_VERSIONS),
    help="Matter specification version used to generate the data model",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
@click.option("--no-colored-logs", is_flag=True, help="Disable colored logs")
@click.option(
    "--skip-xml-parsing",
    is_flag=True,
    help="Skip XML parsing and reuse existing JSON intermediates",
)
@click.option(
    "--skip-code-generation",
    is_flag=True,
    help="Skip code generation and only refresh JSON intermediates",
)
@click.option(
    "--clean", is_flag=True, help="Remove previously generated sources before running"
)
def main(
    output_dir: str,
    cluster_file: str,
    device_file: str,
    cluster_dir: str,
    device_dir: str,
    chip_version: str,
    verbose: bool,
    no_colored_logs: bool,
    skip_xml_parsing: bool,
    skip_code_generation: bool,
    clean: bool,
) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logger(log_level, not no_colored_logs)

    esp_dir = os.getenv("ESP_MATTER_PATH")
    VERIFY_OR_EXIT(
        esp_dir is not None, "ESP_MATTER_PATH environment variable is not set"
    )

    chip_path = os.path.join(esp_dir, "connectedhomeip", "connectedhomeip")

    if not cluster_dir or not device_dir:
        default_xml_input_dir = os.path.join(chip_path, "data_model", chip_version)
        VERIFY_OR_EXIT(
            os.path.exists(default_xml_input_dir),
            f"Data model directory for version {chip_version} does not exist: {default_xml_input_dir}",
        )
        cluster_dir = os.path.join(default_xml_input_dir, "clusters")
        device_dir = os.path.join(default_xml_input_dir, "device_types")
    VERIFY_OR_EXIT(
        os.path.exists(cluster_dir),
        f"Clusters directory does not exist: {cluster_dir}",
    )
    VERIFY_OR_EXIT(
        os.path.exists(device_dir),
        f"Device types directory does not exist: {device_dir}",
    )

    data_model_gen_config = DataModelGenConfig(
        esp_matter_path=esp_dir,
        output_dir=output_dir,
        json_output_dir=DEFAULT_OUTPUT_DIR,
        chip_version=chip_version,
        cluster_dir=cluster_dir,
        device_dir=device_dir,
        cluster_file=cluster_file or None,
        device_file=device_file or None,
        skip_xml_parsing=skip_xml_parsing,
        skip_code_generation=skip_code_generation,
        clean_output=clean or False,
    )

    try:
        generator = DataModelGenerator(data_model_gen_config)
        generator.run()
    except Exception as exc:
        raise Exception(f"Error during data model generation: {str(exc)}") from exc


if __name__ == "__main__":
    main()
