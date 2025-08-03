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
from enum import Enum
from colorlog import ColoredFormatter
import sys

DEFAULT_OUTPUT_DIR = "out"
DEFAULT_CHIP_VERSION = "1.5"

SPECIFICATION_VERSIONS = ["1.1", "1.2", "1.3", "1.4", "1.4.2", "1.5"]

try:
    DEFAULT_DATA_MODEL_DIR = os.path.join(
        os.getenv("ESP_MATTER_PATH"), "components", "esp_matter", "data_model"
    )
except Exception as e:
    raise Exception(f"ESP_MATTER_PATH is not set: {e}")

# Use %(filename)s instead of %(pathname)s to get just the filename
log_format_string = "[%(levelname)s] %(filename)s:%(lineno)d: %(message)s"

colored_formatter = ColoredFormatter(
    "%(log_color)s" + log_format_string,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)


def setup_logger(log_level="INFO", is_colored=False):
    """
    Sets up a logger with the specified level and color formatting.

    Args:
        log_level: Logging level to use
        is_colored: Whether to use colored output
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    stream_handler = logging.StreamHandler(sys.stdout)

    if is_colored:
        stream_handler.setFormatter(colored_formatter)
    else:
        stream_handler.setFormatter(logging.Formatter(log_format_string))

    root_logger.addHandler(stream_handler)


class FileNames(Enum):
    """Enum for file names used by the data model generation tool"""

    INTERNALLY_MANAGED_ATTRIBUTES = "internally_managed_attributes.json"
    DELEGATE_CLUSTERS = "delegate_clusters.json"
    PLUGIN_INIT_CB_CLUSTERS = "plugin_init_cb_clusters.json"
    CLUSTER_MAPPING = "cluster_mapping.json"
    MIGRATED_CLUSTERS = "migrated_clusters.json"
    ZAP_FILTER_LIST = "zap_filter_list.json"
    CLUSTER_JSON = "clusters.json"
    DEVICE_JSON = "device_types.json"
