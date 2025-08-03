# Matter Data Model Generator Tool

This tool generates C++ header and source files for Matter clusters and device types directly from Matter specification XML files. 

## Overview

The generator performs two main steps:
1. **XML Processing**: Parses Matter specification XML files to generate intermediate JSON representations
2. **Code Generation**: Uses the intermediate JSON files to generate C++ header and source files

## Prerequisites

- ESP-Matter repository cloned
- `ESP_MATTER_PATH` environment variable set to your ESP-Matter repository path

## Installation

```bash
# Clone ESP-Matter if you haven't already
git clone --recursive https://github.com/espressif/esp-matter.git

# Set environment variable
export ESP_MATTER_PATH=/path/to/esp-matter/

# Install required Python packages
cd $ESP_MATTER_PATH/tools/data_model_gen
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Run the complete generation process
# Data Model files generated with default 1.5 Matter specification.
python main.py
```

This will:
1. Parse all Matter XML files from the default location (`connectedhomeip/data_model/1.5`)
2. Generate intermediate JSON files in (`out`) directory
3. Generate C++ header and source files in the default output directory (`$ESP_MATTER_PATH/components/esp_matter/data_model/`)

## Generated Files

### Intermediate JSON Files

The tool generates following intermediate JSON files during processing:

- `clusters.json`: Contains clusters with their attributes, commands, events, and other data
- `device_types.json`: Contains device types with their required clusters
- `delegate_clusters.json`: Lists clusters with delegates
- `internally_managed_attributes.json`: Lists attributes managed by ConnectedHomeIP
- `plugin_init_cb_clusters.json`: Lists clusters with plugin init callbacks
- `zap_filter_list.json`: Filters attributes, commands, events based on ZAP XML files
- `migrated_clusters.json`: Lists clusters migrated to the code-driven approach

### Output C++ Files

For each cluster and device type, the tool generates:

- **Cluster files**: `on_off.h` and `on_off.cpp` from `on_off.xml`
- **Device files**: `extended_color_light.h` and `extended_color_light.cpp` from `extended_color_light.xml`

These files are organized in the output directory structure:
```
<output>/
├── clusters/
│   ├── on_off/
│   │   ├── on_off.h
│   │   └── on_off.cpp
│   └── ...
└── device_types/
    ├── extended_color_light_device/
    │   ├── extended_color_light.h
    │   └── extended_color_light.cpp
    └── ...
```