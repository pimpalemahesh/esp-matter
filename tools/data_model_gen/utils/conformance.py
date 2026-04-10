# Copyright 2026 Espressif Systems (Shanghai) PTE LTD
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
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

SUPPORTED_CONFORMANCE_TAGS = {
    "mandatoryConform",
    "optionalConform",
    "otherwiseConform",
    "deprecateConform",
    "disallowConform",
    "provisionalConform",
    "describedConform",
}


class ConformanceException(Exception):
    """Exception raised when conformance parsing fails"""

    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class ConformanceDecision(Enum):
    MANDATORY = auto()
    OPTIONAL = auto()
    OTHERWISE = auto()
    DEPRECATED = auto()
    DISALLOWED = auto()
    PROVISIONAL = auto()
    DESCRIBED = auto()
    NOT_APPLICABLE = auto()

    def to_string(self):
        return self.name.lower()


class ConformanceTAG(Enum):
    FEATURE = "feature"
    ATTRIBUTE = "attribute"
    COMMAND = "command"
    COMMAND_FLAG = "flag"
    EVENT = "event"
    CONDITION = "condition"
    GREATER = "greater"
    EQUAL = "equal"
    TRUE = "true"
    FALSE = "false"
    NON = "non"
    NOT = "not"
    AND = "and"
    OR = "or"


def get_conformance_type(type: str) -> ConformanceDecision:
    if type == "mandatory" or type == "mandatoryConform":
        return ConformanceDecision.MANDATORY
    elif type == "optional" or type == "optionalConform":
        return ConformanceDecision.OPTIONAL
    elif type == "otherwise" or type == "otherwiseConform":
        return ConformanceDecision.OTHERWISE
    elif type == "deprecated" or type == "deprecateConform":
        return ConformanceDecision.DEPRECATED
    elif type == "disallow" or type == "disallowConform":
        return ConformanceDecision.DISALLOWED
    elif type == "provisional" or type == "provisionalConform":
        return ConformanceDecision.PROVISIONAL
    elif type == "described" or type == "describedConform":
        return ConformanceDecision.DESCRIBED
    else:
        logger.warning(f"Unknown conformance type: {type}")
        return ConformanceDecision.NOT_APPLICABLE


@dataclass(frozen=True)
class Choice:
    marker: str = None
    more: bool = False

    def __str__(self):
        marker_str = self.marker if self.marker else ""
        more_str = "+" if self.more else ""
        return marker_str + more_str

    def to_dict(self):
        result = {}
        if self.marker:
            result["choice"] = self.marker
        if self.more:
            result["more"] = self.more
            result["min"] = 1
        return result


@dataclass
class BaseConformance:
    """Base class for conformance."""

    type: ConformanceDecision = None
    choice: Optional[Choice] = None
