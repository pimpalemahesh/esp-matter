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
import click
from dataclasses import dataclass
from datetime import datetime

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
    # "on_off_light",
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
    "bridged_node",
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
    "mode_select_device",
    # "room_ac",
    # "temp_ctrl_cabinet",
    # "refrigerator",
    # "air_purifier",
    # "air_quality_sensor",
    # "robotic_vacuum_cleaner",
    # "laundry_washer",
    # "dish_washer",
    "smoke_co_alarm",
    # "water_leak_detector",
    # "water_freeze_detector",
    "power_source",
    # "rain_sensor",
    # "electrical_sensor",
    # "oven",
    "cooktop",
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


@dataclass
class ContextArgs:
    device_types: list[str]
    retry_attempts: int
    storage_path: str
    pytest_path: str
    serial_port: str
    baudrate: int
    wifi_ssid: str
    wifi_passphrase: str
    manual_code: str
    allow_provisional: bool


test_commands = [
    {
        "script": "TC_DeviceConformance.py",
        "args": {
            "--manual-code": MANUAL_CODE,
            "--tests": "test_TC_IDM_10_2",
            "--bool-arg": "allow_provisional:true",
            "timeout": 10000,
        },
    },
    {
        "script": "TC_DeviceBasicComposition.py",
        "args": {
            "--manual-code": MANUAL_CODE,
            "--tests": "test_TC_IDM_10_1",
            "timeout": 10000,
        },
    },
    # {
    #     "script": "TC_RR_1_1.py",
    #     "args": {
    #         "-m": "ble-wifi",
    #         "-p": "20202021",
    #         "-d": "3840",
    #         "--wifi-ssid": WIFI_SSID,
    #         "--wifi-passphrase": WIFI_PASSPHRASE,
    #         "--int-arg": "use_pase_only:0",
    #         "-c": "/tmp",
    #         "timeout": 10000,
    #     },
    # },
]


def send_serial_command(ser, command, wait_time=2):
    """Send a command to the device via serial port and return response"""
    clean_command = command.strip()
    print(f"Sending command: {clean_command}")

    ser.write((clean_command + "\r\n").encode("ascii"))
    time.sleep(wait_time)

    response = b""
    while ser.in_waiting > 0:
        response += ser.read(ser.in_waiting)
        time.sleep(0.1)

    decoded_response = response.decode("utf-8", errors="ignore").strip()

    if decoded_response:
        print(f"Response: {decoded_response}")

    return decoded_response

def factory_reset_device(ser):
    """Factory reset the device"""
    print("Factory resetting device...")
    send_serial_command(ser, "matter esp factoryreset", wait_time=10)


def create_device(ser, device_type):
    """Create a device of the specified type, retry once on failure"""
    print(f"Creating device type: {device_type}")

    response = send_serial_command(
        ser,
        f"create --device_type {device_type}",
        wait_time=5
    )

    # Define what "failure" looks like
    failed = (
        not response or
        "error" in response.lower() or
        "fail" in response.lower()
    )

    if failed:
        print("retrying once more time")
        time.sleep(1)

        response = send_serial_command(
            ser,
            f"create --device_type {device_type}",
            wait_time=5
        )

        # if not response or "error" in response.lower():
        #     print("Retry failed.")
        #     return False

    print("Device created successfully.")
    return True

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
    final_result = "PASS"
    final_output = {}
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
        final_output = {k: int(v) for k, v in match.groupdict().items()}
        if final_output["Passed"] > 0:
            final_result = "PASS"
        else:
            final_result = "FAIL"
    # Fallback: check for "Final result: PASS !"
    if "Final result: FAIL !" in test_output:
        final_result = "FAIL"
        final_output = {}
    return final_result, final_output


def extract_artifacts_path(test_output):
    """Extract artifacts path from test output"""
    # Look for: "Artifacts are saved in "/path/to/artifacts""
    pattern = r'Artifacts are saved in "([^"]+)"'
    match = re.search(pattern, test_output)
    if match:
        return match.group(1)
    return None


def collect_artifacts(
    artifacts_source_path, device_storage_path, test_name, test_output=""
):
    """Collect and organize artifacts from test run"""
    try:
        # Map test scripts to artifact file names
        artifact_mapping = {
            "TC_DeviceConformance.py": "device_conformance_logs.txt",
            "TC_DeviceBasicComposition.py": "device_composition_logs.txt",
            # "TC_RR_1_1.py": "tc_rr_logs.txt",
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
                    if file.endswith((".log", ".txt", ".yaml")):
                        src_file = os.path.join(root, file)
                        try:
                            with open(src_file, "r", errors="ignore") as f:
                                content = f.read()
                                if content.strip():  # Only add non-empty files
                                    all_logs.append(
                                        f"=== {file} (from {os.path.relpath(root, artifacts_source_path)}) ===\n"
                                    )
                                    all_logs.append(content)
                                    all_logs.append("\n\n")
                        except Exception as e:
                            print(f"Error reading {src_file}: {e}")

        # Write combined logs to artifact file
        with open(artifact_dest, "w", errors="ignore") as f:
            if all_logs:
                f.write("".join(all_logs))
            else:
                f.write(f"No artifacts found for {test_name}\n")
        print(f"Artifacts saved to: {artifact_dest}")

    except Exception as e:
        print(f"Error collecting artifacts: {e}")
        import traceback

        traceback.print_exc()


def execute_test_command(
    ser, device_type, full_command, device_storage_path, test_name, retry_attempts=1
):
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
            collect_artifacts(
                artifacts_path, device_storage_path, test_name, test_output
            )
            clean_environment()
            time.sleep(2)
            return "PASS"
        else:
            print(f"Test failed on attempt {attempt + 1}.")
            if result_details:
                print(
                    f"  Details: Executed={result_details.get('Executed', 0)}, "
                    f"Passed={result_details.get('Passed', 0)}, "
                    f"Failed={result_details.get('Failed', 0)}, "
                    f"Error={result_details.get('Error', 0)}"
                )
            time.sleep(10)
            if attempt < retry_attempts - 1:
                clean_environment()
                factory_reset_device(ser)
                time.sleep(2)
                create_device(ser, device_type)
                time.sleep(2)

    # Collect artifacts even on failure
    collect_artifacts(artifacts_path, device_storage_path, test_name, test_output)

    return "FAIL"


def run_tests_for_all_devices(context: ContextArgs):
    """Run tests for all device types"""
    device_types = context.device_types
    # Open serial connection
    try:
        ser = serial.Serial(context.serial_port, context.baudrate, timeout=1)
        print(f"Connected to {context.serial_port} at {context.baudrate} baud")
        time.sleep(2)  # Wait for connection to stabilize
    except Exception as e:
        print(f"Failed to open serial port: {e}")
        return

    # Create main results table
    main_results = PrettyTable()
    main_results.field_names = [
        "Device Type",
        "Test 1 (TC_DeviceConformance)",
        "Test 2 (TC_DeviceBasicComposition)",
        # "Test 3 (TC_RR_1_1)",
        "Overall",
    ]

    try:
        for device_type in device_types:
            print(f"\n{'='*80}")
            print(f"Testing device type: {device_type}")
            print(f"{'='*80}")

            # Create device-specific storage path
            if not os.path.exists(context.storage_path):
                os.makedirs(context.storage_path, exist_ok=True)
            device_storage_path = os.path.join(context.storage_path, device_type)
            os.makedirs(device_storage_path, exist_ok=True)

            # Factory reset device
            factory_reset_device(ser)

            # Wait for device to be ready
            time.sleep(5)

            # Run each test command
            test_results = []
            for idx, test_command in enumerate(test_commands, start=1):
                print(f"\n--- Creating device {device_type} ---")
                create_device(ser, device_type)
                time.sleep(5)
                print(f"\n--- Running Test {idx}: {test_command['script']} ---")
                full_command = f"cd {context.pytest_path} && {load_test_command(test_command, device_storage_path)}"
                result = execute_test_command(
                    ser, device_type, full_command, device_storage_path, test_command["script"]
                )
                test_results.append(result)
                time.sleep(2)
                factory_reset_device(ser)
                time.sleep(2)
                clean_environment()
                time.sleep(2)

            # Determine overall result
            overall = "PASS" if all(r == "PASS" for r in test_results) else "FAIL"

            # Add row to results table
            main_results.add_row(
                [
                    device_type,
                    test_results[0],
                    test_results[1],
                    # test_results[2],
                    overall,
                ]
            )

            print(f"\nDevice {device_type} test results:")
            print(f"  Test 1: {test_results[0]}")
            print(f"  Test 2: {test_results[1]}")
            # print(f"  Test 3: {test_results[2]}")
            print(f"  Overall: {overall}")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        ser.close()
        print("\n" + "=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        print(main_results)

        # Calculate summary statistics
        total_devices = len(main_results._rows) if main_results._rows else 0
        passed_devices = (
            sum(1 for row in main_results._rows if row[-1] == "PASS")
            if main_results._rows
            else 0
        )
        failed_devices = total_devices - passed_devices

        print(f"\nSummary:")
        print(f"  Total devices tested: {total_devices}")
        print(f"  Passed: {passed_devices}")
        print(f"  Failed: {failed_devices}")

        # Save results to file
        results_file = os.path.join("out", f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_test_results.txt")
        with open(results_file, "w") as f:
            f.write("Device Type Test Results\n")
            f.write("=" * 80 + "\n")
            f.write(str(main_results))
            f.write(f"\n\nSummary:\n")
            f.write(f"  Total devices tested: {total_devices}\n")
            f.write(f"  Passed: {passed_devices}\n")
            f.write(f"  Failed: {failed_devices}\n")
        print(f"\nResults saved to: {results_file}")


@click.command()
@click.option("--device-type", type=str, default=None, show_default=True)
@click.option("--retry-attempts", type=int, default=1, show_default=True)
@click.option("--storage-path", type=str, default="out", show_default=True)
@click.option("--pytest-path", type=str, default=PYTEST_PATH, show_default=True)
@click.option("--serial-port", type=str, default=SERIAL_PORT, show_default=True)
@click.option("--baudrate", type=int, default=BAUDRATE, show_default=True)
@click.option("--wifi-ssid", type=str, default=WIFI_SSID, show_default=True)
@click.option("--wifi-passphrase", type=str, default=WIFI_PASSPHRASE, show_default=True)
@click.option("--manual-code", type=str, default=MANUAL_CODE, show_default=True)
@click.option("--allow-provisional", is_flag=True, help="Allow provisional tests")
def main(
    device_type,
    retry_attempts,
    storage_path,
    pytest_path,
    serial_port,
    baudrate,
    wifi_ssid,
    wifi_passphrase,
    manual_code,
    allow_provisional,
):

    device_type_list = DEVICE_TYPES

    if device_type is not None:
        device_type_list = [device_type]
    ctx = ContextArgs(
        device_types=device_type_list,
        retry_attempts=retry_attempts,
        storage_path=storage_path,
        pytest_path=pytest_path,
        serial_port=serial_port,
        baudrate=baudrate,
        wifi_ssid=wifi_ssid,
        wifi_passphrase=wifi_passphrase,
        manual_code=manual_code,
        allow_provisional=allow_provisional,
    )

    run_tests_for_all_devices(ctx)


if __name__ == "__main__":
    main()
