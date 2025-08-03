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
from .conformance_parser import (
    check_conformance_restrictions,
    parse_conformance,
)
from .elements import Cluster, Command
from utils.helper import check_valid_id, safe_get_attr

logger = logging.getLogger(__name__)


class CommandParser:
    """Class for parsing command data"""

    def __init__(
        self, cluster: Cluster, feature_map: dict, allowed_commands_ids: list = []
    ):
        self.cluster = cluster
        self.feature_map = feature_map if feature_map else {}
        self.processed_commands = set()
        self.allowed_commands_ids = allowed_commands_ids if allowed_commands_ids else []

    def parse(self, root, base_commands: list[Command] = None):
        """Iterate over all command elements in the cluster xml file and create Command objects.

        :param root: The root element of the cluster XML file.
        :param base_commands: The base commands.
        :param base_commands: list[Command]:  (Default value = None)

        """
        for command in root.findall("commands/command"):
            if not self._should_process_command(command, base_commands):
                continue

            logger.debug(f"Processing command {command.get('name')} for cluster {safe_get_attr(self.cluster, 'name')}")
            cmd = self._create_command(command)
            self._process_command_access(cmd, command)
            cmd.conformance = parse_conformance(command, self.feature_map)
            self._process_command_fields(cmd, command)

            self.cluster.commands.add(cmd)

            if self.cluster.skip_command_cb:
                cmd.skip_command_cb = True
                continue

        # Add base commands to the cluster if they are not already in the cluster
        if base_commands:
            for base_command in base_commands:
                if base_command.name not in self.processed_commands:
                    self.cluster.commands.add(base_command)

        logger.debug(
            f"Processed {len(self.cluster.commands)} commands for cluster {safe_get_attr(self.cluster, 'name')}"
        )

    def _should_process_command(self, command, base_commands: list[Command] = None):
        """Check if command should be processed

        :param command: The command element from the cluster XML file.
        :param base_commands: list[Command]:  (Default value = None)
        :returns: True if the command should be processed, False otherwise.

        """
        command_name = command.get("name")
        if not command_name:
            logger.debug(f"Skipping - missing command name {command}")
            return False
        if command_name in self.processed_commands:
            return False
        self.processed_commands.add(command_name)
        if base_commands:
            base_command = next(
                (cmd for cmd in base_commands if cmd.name == command_name), None
            )
            if not command.get("id") and base_command:
                command.set("id", base_command.id)
        command_id = command.get("id")
        if not check_valid_id(command_id):
            return False

        if not (command_name and command_id):
            logger.debug(f"Skipping - missing name or id {command_name} {command_id}")
            return False
        if (
            self.allowed_commands_ids
            and int(command_id, 16) not in self.allowed_commands_ids
        ):
            logger.debug(
                f"Skipping - command {command_name} id {int(command_id, 16)} not in allowed commands"
            )
            return False

        if command_name in [safe_get_attr(c, "name") for c in self.processed_commands]:
            logger.debug(
                f"Skipping - command already exists in processed commands {command_name}"
            )
            return False

        if check_conformance_restrictions(self.feature_map, command):
            logger.debug(
                f"Skipping - command {command.get('name', 'unknown')} due to conformance restrictions"
            )
            return False

        return True

    def _create_command(self, command):
        """Create a Command object

        :param command:
        :returns: The created Command object.

        """
        command_name = command.get("name")
        cmd = Command(
            id=command.get("id"),
            name=command_name,
            direction=command.get("direction"),
            response=command.get("response"),
            is_mandatory=command.find("mandatoryConform") is not None,
        )
        if safe_get_attr(self.cluster, "command_handler_available") or safe_get_attr(self.cluster, "is_migrated_cluster"):
            cmd.command_handler_available = True
        return cmd

    def _process_command_access(self, cmd, command):
        """Process command access

        :param cmd: The command object to process.
        :param command: The command element from the cluster XML file.

        """
        access_elem = command.find("access")
        if access_elem is not None:
            cmd_access = Command.CommandAccess(
                invokePrivilege=access_elem.get("invokePrivilege", None),
                timed=(
                    True
                    if access_elem.get("timed") and access_elem.get("timed") == "true"
                    else False
                ),
                fabric_scoped=(
                    True
                    if access_elem.get("fabricScoped")
                    and access_elem.get("fabricScoped") == "true"
                    else False
                ),
            )
            cmd.set_access(cmd_access)

    def _process_command_fields(self, cmd, command):
        """Process command fields

        :param cmd: The command object to process.
        :param command: The command element from the cluster XML file.

        """
        for field_elem in command.findall("field"):
            field_id = field_elem.get("id")
            field_name = field_elem.get("name")
            field_type = field_elem.get("type")
            field_default = field_elem.get("default")

            # Check if field should be processed
            if not field_id or not field_name or not field_type:
                continue

            # Process field constraints
            constraint = None
            constraint_elem = field_elem.find("constraint")
            if constraint_elem is not None:
                constraint = {}
                # Handle different constraint types
                for child in constraint_elem:
                    if child.tag == "maxLength":
                        constraint["type"] = "maxLength"
                        constraint["value"] = child.get("value")
                    elif child.tag == "min":
                        constraint["type"] = "min"
                        constraint["value"] = child.get("value")
                    elif child.tag == "max":
                        constraint["type"] = "max"
                        constraint["value"] = child.get("value")
                    elif child.tag == "between":
                        constraint["type"] = "between"
                        from_elem = child.find("from")
                        to_elem = child.find("to")

                        if from_elem is not None and from_elem.get("value") is not None:
                            constraint["min"] = from_elem.get("value")
                        else:
                            constraint["min"] = "0"

                        if to_elem is not None and to_elem.get("value") is not None:
                            constraint["max"] = to_elem.get("value")
                        else:
                            constraint["max"] = "0"
                    elif child.tag == "desc":
                        constraint["type"] = "desc"
                        constraint["value"] = None

            field = Command.CommandField(
                id=field_id,
                name=field_name,
                type_=field_type,
                default_value=field_default,
                is_mandatory=field_elem.find("mandatoryConform") is not None,
                constraint=constraint,
            )
            cmd.add_field(field)
