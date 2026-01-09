# Matter Device Data Model Validator


An UI tool for validating Matter device data models against official Matter specifications.

## 📋 Overview

This tool parses wildcard logs from Matter devices and validates the data model against official Matter specifications. It helps identify data model compliance issues early in the development process.

Internally it uses esp-matter-dm-validator as a python module to validate data model.
check this [https://github.com/espressif/esp-matter-tools/tree/main/dmv_tool] for more information.

### ⚠️ Important Note

This is an experimental feature and does not guarantee full compliance with Matter specifications. It is intended to assist developers in identifying data model issues early in the development process.

## 🔍 Validation Scope

### ✅ What This Tool Validates

- **Device Type & Cluster Revisions**: Verifies correct revision numbers for device types and clusters
- **Mandatory Clusters**: Checks that all mandatory clusters required by the device type are present
- **Mandatory Attributes & Commands**: Validates that all mandatory attributes and commands are implemented
- **Mandatory Features**: Confirms required features for specific device types are implemented
  (e.g., lighting feature required for level control cluster on extended color light device type)
- **Optional Feature Dependencies**: Validates required attributes and commands when optional features are enabled
  (Limited to single feature dependencies only)

### ⚠️ What This Tool Does NOT Validate

- **Optional Elements**: Optional clusters, attributes, commands, and events beyond mandatory requirements
- **Attribute Values**: Actual values and their bounds are not validated
- **Events**: Not present in wildcard logs, only warnings shown for mandatory events
- **Multiple Feature Dependencies**: Attributes and commands that depend on multiple features
  (e.g., UnoccupiedCoolingSetpoint attribute requires both COOL and OCC features)
