# SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD

# SPDX-License-Identifier: Apache-2.0

import pathlib
import re
import subprocess
import serial
import os
import shutil
import glob
from prettytable import PrettyTable
import json
import time

PYTEST_PATH = "/home/mahesh/code/connectedhomeip/src/python_testing"
current_dir = os.path.dirname(os.path.abspath(__file__))

MANUAL_CODE = "34970112332"
STORAGE_PATH = current_dir
WIFI_SSID = "ESP_India"
WIFI_PASSPHRASE = "Esp@3101"
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200



# Device types from device_types.h (excluding ESP_MATTER_DEVICE_TYPE_MAX)
DEVICE_TYPES = [
    "on_off_light",
    # "dimmable_light",
    # "color_temperature_light",
    # "extended_color_light",
    # "on_off_light_switch",
    # "dimmer_switch",
    # "color_dimmer_switch",
    # "generic_switch",
    # "on_off_plug_in_unit",
    # "dimmable_plug_in_unit",
    # "fan",
    # "thermostat",
    # "aggregator",
    # "bridged_node",
    # "control_bridge",
    # "door_lock",
    # "window_covering",
    # "temperature_sensor",
    # "humidity_sensor",
    # "occupancy_sensor",
    # "contact_sensor",
    # "light_sensor",
    # "pressure_sensor",
    # "flow_sensor",
    # "pump",
    # "mode_select_device",
    # "room_ac",
    # "temp_ctrl_cabinet",
    # "refrigerator",
    # "air_purifier",
    # "air_quality_sensor",
    # "robotic_vacuum_cleaner",
    # "laundry_washer",
    # "dish_washer",
    # "smoke_co_alarm",
    # "water_leak_detector",
    # "water_freeze_detector",
    # "power_source",
    # "rain_sensor",
    # "electrical_sensor",
    # "oven",
    # "cooktop",
    # "energy_evse",
    # "microwave_oven",
    # "extractor_hood",
    # "laundry_dryer",
    # "water_valve",
    # "device_energy_management",
    # "pump_controller",
    # "thread_border_router",
    # "mounted_on_off_control",
    # "mounted_dimmable_load_control",
    # "water_heater",
    # "solar_power",
    # "battery_storage",
    # "heat_pump",
    # "chime",
    # "thermostat_controller",
    # "closure_controller",
    # "closure",
    # "closure_panel",
    # "electrical_energy_tariff",
    # "electrical_meter",
    # "electrical_utility_meter",
]

test_commands = [
    {
        "script": "TC_DeviceConformance.py",
        "args": {"--manual-code": MANUAL_CODE, "--tests": "test_TC_IDM_10_2", "--bool-arg": "allow_provisional:true", "timeout": 10000}
    },
    {
        "script": "TC_DeviceBasicComposition.py",
        "args": {"--manual-code": MANUAL_CODE, "--tests": "test_TC_IDM_10_1", "timeout": 10000}
    },
    {
        "script": "TC_RR_1_1.py",
        "args": {"-m": "ble-wifi", "-p": "20202021", "-d": "3840", "--wifi-ssid": WIFI_SSID, "--wifi-passphrase": WIFI_PASSPHRASE, "--int-arg": "use_pase_only:0", "-c": "/tmp", "timeout": 10000}
    }
]

def send_serial_command(ser, command, wait_time=2):
    """Send a command to the device via serial port"""
    print(f"Sending command: {command}")
    ser.write(f"{command}\r\n".encode())
    time.sleep(wait_time)
    # Read any response
    response = b""
    while ser.in_waiting > 0:
        response += ser.read(ser.in_waiting)
        time.sleep(0.1)
    if response:
        print(f"Response: {response.decode('utf-8', errors='ignore')}")

def factory_reset_device(ser):
    """Factory reset the device"""
    print("Factory resetting device...")
    send_serial_command(ser, "matter esp factoryreset", wait_time=10)

def create_device(ser, device_type):
    """Create a device of the specified type"""
    print(f"Creating device type: {device_type}")
    send_serial_command(ser, f"create --device_type {device_type}", wait_time=5)

def load_test_command(test_command, device_storage_path):
    """Build the full test command with storage path"""
    command = "python3 "
    command += test_command["script"]
    # Add storage path
    command += f" --storage-path {device_storage_path}"
    # Add other arguments
    for key, value in test_command["args"].items():
        if key == "timeout":
            continue  # Skip timeout as it's not a command line arg
        if isinstance(value, bool):
            if value:
                command += f" {key}"
        else:
            command += f" {key} {value}"
    return command

def clean_environment():
    """Clean up test environment"""
    clean_up_command = "rm -rf /tmp/chip_*"
    subprocess.getoutput(clean_up_command)

def parse_test_results(test_output):
    """Parse test results from output string"""
    # Look for test summary line: "Test results: Error X, Executed Y, Failed Z, Passed W, Requested V, Skipped U"
    pattern = re.compile(
        r"Test results:\s*"
        r"Error\s+(?P<Error>\d+),\s*"
        r"Executed\s+(?P<Executed>\d+),\s*"
        r"Failed\s+(?P<Failed>\d+),\s*"
        r"Passed\s+(?P<Passed>\d+),\s*"
        r"Requested\s+(?P<Requested>\d+),\s*"
        r"Skipped\s+(?P<Skipped>\d+)"
    )
    match = pattern.search(test_output)
    if match:
        results = {k: int(v) for k, v in match.groupdict().items()}
        if results["Passed"] > 0:
            return "PASS", results
        else:
            return "FAIL", results
    # Fallback: check for "Final result: PASS !"
    if "INFO:root:Final result: PASS !" in test_output or "Final result: PASS !" in test_output:
        return "PASS", {}
    return "FAIL", {}

def extract_artifacts_path(test_output):
    """Extract artifacts path from test output"""
    # Look for: "Artifacts are saved in "/path/to/artifacts""
    pattern = r'Artifacts are saved in "([^"]+)"'
    match = re.search(pattern, test_output)
    if match:
        return match.group(1)
    return None

def collect_artifacts(artifacts_source_path, device_storage_path, test_name, test_output=""):
    """Collect and organize artifacts from test run"""
    try:
        # Map test scripts to artifact file names
        artifact_mapping = {
            "TC_DeviceConformance.py": "device_conformance_logs.txt",
            "TC_DeviceBasicComposition.py": "device_composition_logs.txt",
            "TC_RR_1_1.py": "tc_rr_logs.txt"
        }
        
        artifact_filename = artifact_mapping.get(test_name, f"{test_name}_logs.txt")
        artifact_dest = os.path.join(device_storage_path, artifact_filename)
        
        # Start with test output
        all_logs = []
        if test_output:
            all_logs.append("=== Test Output ===\n")
            all_logs.append(test_output)
            all_logs.append("\n\n")
        
        # Collect logs from artifacts directory if it exists
        if artifacts_source_path and os.path.exists(artifacts_source_path):
            # Look for all log and text files in the artifacts directory
            for root, dirs, files in os.walk(artifacts_source_path):
                for file in files:
                    if file.endswith(('.log', '.txt', '.yaml')):
                        src_file = os.path.join(root, file)
                        try:
                            with open(src_file, 'r', errors='ignore') as f:
                                content = f.read()
                                if content.strip():  # Only add non-empty files
                                    all_logs.append(f"=== {file} (from {os.path.relpath(root, artifacts_source_path)}) ===\n")
                                    all_logs.append(content)
                                    all_logs.append("\n\n")
                        except Exception as e:
                            print(f"Error reading {src_file}: {e}")
        
        # Write combined logs to artifact file
        with open(artifact_dest, 'w', errors='ignore') as f:
            if all_logs:
                f.write("".join(all_logs))
            else:
                f.write(f"No artifacts found for {test_name}\n")
        print(f"Artifacts saved to: {artifact_dest}")
        
        # Collect device_side_logs.txt - append mode to combine logs from all tests
        device_side_logs_dest = os.path.join(device_storage_path, "device_side_logs.txt")
        device_log_content = []
        
        # Try to find device_side_logs.txt in artifacts directory
        if artifacts_source_path and os.path.exists(artifacts_source_path):
            for root, dirs, files in os.walk(artifacts_source_path):
                if "device_side_logs.txt" in files:
                    device_side_logs_src = os.path.join(root, "device_side_logs.txt")
                    try:
                        with open(device_side_logs_src, 'r', errors='ignore') as f:
                            content = f.read()
                            if content.strip():
                                device_log_content.append(f"=== Device logs from {test_name} ===\n")
                                device_log_content.append(content)
                                device_log_content.append("\n")
                        break
                    except Exception as e:
                        print(f"Error reading device_side_logs.txt: {e}")
        
        # Append to device_side_logs.txt (create if doesn't exist)
        mode = 'a' if os.path.exists(device_side_logs_dest) else 'w'
        with open(device_side_logs_dest, mode, errors='ignore') as f:
            if device_log_content:
                f.write("".join(device_log_content))
            elif mode == 'w':  # Only write placeholder if creating new file
                f.write(f"Device side logs for {test_name}\n")
                f.write("Note: Device logs may be included in the test-specific log files above.\n")
                f.write("="*80 + "\n")
    
    except Exception as e:
        print(f"Error collecting artifacts: {e}")
        import traceback
        traceback.print_exc()

def execute_test_command(full_command, device_storage_path, test_name, retry_attempts=1):
    """Execute a test command and return PASS/FAIL, also collect artifacts"""
    artifacts_path = None
    test_output = ""
    for attempt in range(retry_attempts):
        print(f"Attempt {attempt + 1} for command: {full_command}")
        test_out_str = subprocess.getoutput(full_command)
        test_output = test_out_str  # Keep the latest output
        print(f"Test output: {test_out_str}")
        
        # Parse test results
        result, result_details = parse_test_results(test_out_str)
        
        # Extract artifacts path
        if not artifacts_path:
            artifacts_path = extract_artifacts_path(test_out_str)
        
        if result == "PASS":
            print(f"Test passed on attempt {attempt + 1}.")
            # Collect artifacts
            collect_artifacts(artifacts_path, device_storage_path, test_name, test_output)
            clean_environment()
            time.sleep(5)
            return "PASS"
        else:
            print(f"Test failed on attempt {attempt + 1}.")
            if result_details:
                print(f"  Details: Executed={result_details.get('Executed', 0)}, "
                      f"Passed={result_details.get('Passed', 0)}, "
                      f"Failed={result_details.get('Failed', 0)}, "
                      f"Error={result_details.get('Error', 0)}")
            time.sleep(10)
            if attempt < retry_attempts - 1:
                clean_environment()
    
    # Collect artifacts even on failure
    collect_artifacts(artifacts_path, device_storage_path, test_name, test_output)
    
    return "FAIL"

def run_tests_for_all_devices():
    """Run tests for all device types"""
    # Open serial connection
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Connected to {SERIAL_PORT} at {BAUDRATE} baud")
        time.sleep(2)  # Wait for connection to stabilize
    except Exception as e:
        print(f"Failed to open serial port: {e}")
        return

    # Create main results table
    main_results = PrettyTable()
    main_results.field_names = ["Device Type", "Test 1 (TC_DeviceConformance)", "Test 2 (TC_DeviceBasicComposition)", "Test 3 (TC_RR_1_1)", "Overall"]

    try:
        for device_type in DEVICE_TYPES:
            print(f"\n{'='*80}")
            print(f"Testing device type: {device_type}")
            print(f"{'='*80}")
            
            # Create device-specific storage path
            device_storage_path = os.path.join(STORAGE_PATH, device_type)
            os.makedirs(device_storage_path, exist_ok=True)
            
            # Factory reset device
            factory_reset_device(ser)
            
            # Create device
            create_device(ser, device_type)
            
            # Wait for device to be ready
            time.sleep(5)
            
            # Run each test command
            test_results = []
            for idx, test_command in enumerate(test_commands, start=1):
                print(f"\n--- Running Test {idx}: {test_command['script']} ---")
                full_command = f"cd {PYTEST_PATH} && {load_test_command(test_command, device_storage_path)}"
                result = execute_test_command(full_command, device_storage_path, test_command['script'])
                test_results.append(result)
                
                # Clean environment after each test
                clean_environment()
                time.sleep(2)
            
            # Determine overall result
            overall = "PASS" if all(r == "PASS" for r in test_results) else "FAIL"
            
            # Add row to results table
            main_results.add_row([
                device_type,
                test_results[0],
                test_results[1],
                test_results[2],
                overall
            ])
            
            print(f"\nDevice {device_type} test results:")
            print(f"  Test 1: {test_results[0]}")
            print(f"  Test 2: {test_results[1]}")
            print(f"  Test 3: {test_results[2]}")
            print(f"  Overall: {overall}")
            
            # Factory reset before next device
            factory_reset_device(ser)
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        ser.close()
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(main_results)
        
        # Calculate summary statistics
        total_devices = len(main_results._rows) if main_results._rows else 0
        passed_devices = sum(1 for row in main_results._rows if row[-1] == "PASS") if main_results._rows else 0
        failed_devices = total_devices - passed_devices
        
        print(f"\nSummary:")
        print(f"  Total devices tested: {total_devices}")
        print(f"  Passed: {passed_devices}")
        print(f"  Failed: {failed_devices}")
        
        # Save results to file
        results_file = os.path.join(STORAGE_PATH, "test_results.txt")
        with open(results_file, "w") as f:
            f.write("Device Type Test Results\n")
            f.write("="*80 + "\n")
            f.write(str(main_results))
            f.write(f"\n\nSummary:\n")
            f.write(f"  Total devices tested: {total_devices}\n")
            f.write(f"  Passed: {passed_devices}\n")
            f.write(f"  Failed: {failed_devices}\n")
        print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    run_tests_for_all_devices()
