# Matter Data Model Generator Tool

This tool generates C++ header and source files for Matter clusters and device types directly from Matter specification XML files.

## Overview

The generator performs two main steps:

1. **XML Processing**: Parses Matter specification XML files to generate intermediate JSON representations
2. **Code Generation**: Uses the intermediate JSON files to generate C++ header and source files

## Prerequisites

- ESP-Matter repository cloned with submodule update (Tool will select default xml files from connectedhomeip submodule directory)
- `ESP_MATTER_PATH` environment variable set to your ESP-Matter repository path

## Installation

Follow the steps below to set up **ESP-Matter** and install the required dependencies.

### 1. Clone ESP-Matter

If you haven't already cloned the repository, follow the official guide:

https://preview-docs.espressif.com/projects/esp-matter/en/docs-auto-number/esp32/developing.html#id1

### 2. Set Environment Variable

Set the `ESP_MATTER_PATH` environment variable to point to your local ESP-Matter directory.

````bash
export ESP_MATTER_PATH=/path/to/esp-matter

## Usage

### Basic Usage

```bash
# Run the complete generation process
# Data Model files generated with default 1.5 Matter specification.
python data_model_gen.py
````

This will:

1. Parse all Matter XML files from the default location (`connectedhomeip/data_model/<default_version>`)
2. Generate intermediate JSON files in default (`out`) directory
3. Generate C++ header and source files in the default output directory (`$ESP_MATTER_PATH/components/esp_matter/data_model/generated`)

> **Note:** Generated files may not be properly formatted. Run **pre-commit** to format them before committing.

### Advanced Usage

```bash
# Run --help command for more advanced usage
python data_model_gen.py --help
```
> **Note:** Single device file generation is intended **for testing purposes only** and may not produce compliant device types.
> Example:
> ```bash
> python data_model_gen.py --device-file <device.xml>
> ```
### Module-Specific Scripts

Run module scripts using Python’s module interface (`-m`) from the **project root**.

***Generate XML files***
```bash
python -m xml_processing.xml_parser

For available options:
python -m xml_processing.xml_parser --help
```

***Generate data model source and header files***
```bash
python -m code_generation.code_generator

For available options:
python -m code_generation.code_generator --help
```

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

- **Cluster files**: `on_off.h`, `on_off.cpp` and `on_off_ids.h` from `on_off.xml`
- **Device files**: `extended_color_light.h` and `extended_color_light.cpp` from `extended_color_light.xml`

These files are organized in the output directory structure:

```
<output-dir>/
├── clusters/
│   ├── on_off/
│   │   ├── on_off_ids.h
│   │   └── on_off.h
│   │   └── on_off.cpp
│   └── ...
└── device_types/
    ├── extended_color_light_device/
    │   ├── extended_color_light.h
    │   └── extended_color_light.cpp
    └── ...
```
