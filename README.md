# Matter Device Data Model Validator

A UI-based tool for validating Matter device data models against official Matter specifications, built on top of the `esp-matter-dm-validator` PyPI package.

## 📋 Overview

The Matter Device Data Model Validator parses wildcard logs collected from Matter devices using chip-tool and validates the extracted data model against official Matter XML specifications.

Wildcard logs can be collected using the following command:

```
./chip-tool any read-by-id 0xFFFFFFFF 0xFFFFFFFF <node-id> 0xFFFF > wildcard_logs.txt
```

This tool helps developers identify data model compliance issues early in the development process.

### ⚠️ Important Note

This tool does not guarantee full compliance with Matter specifications. It is intended to assist developers in identifying data model issues early in the development process.

The validator is under active development and does not yet provide complete end-to-end validation of all Matter specification requirements.

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

#### Local Development Setup

1. **Install Dependencies**:
   ```bash
   # Create a virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate
   
   # Install required packages
   pip install -r requirements.txt
   
   # Run http server on port 5000
   python -m http.server 5000
   ```

3. **Access the Application**:
   - Open your browser and navigate to: `http://localhost:5000`

## 🚨 Troubleshooting

### Common Issues

- **"No module named 'flask'"** → Run `pip install -r requirements.txt`
- **"No [TOO] entries found"** → Error in wildcard file format, check your uploaded file
- **"Version X.X not supported"** → This specification version is not supported yet
