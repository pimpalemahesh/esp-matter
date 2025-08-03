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

"""
Custom exception classes for the data model generator.

All exceptions include optional context (file_path, line_number, cluster/device name)
and optional suggestion for fixing the issue to improve error and debug messages.
"""

from typing import Optional


class DataModelGenError(Exception):
    """Base exception for all data model generator errors."""

    def __init__(
        self,
        message: str,
        *,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        context: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.context = context
        self.suggestion = suggestion
        parts = [message]
        if file_path:
            parts.append(f"File: {file_path}")
        if line_number is not None:
            parts.append(f"Line: {line_number}")
        if context:
            parts.append(f"Context: {context}")
        if suggestion:
            parts.append(f"Suggestion: {suggestion}")
        super().__init__(" \n ".join(parts))

    def __str__(self) -> str:
        return self.args[0] if self.args else self.message


class XmlParseError(DataModelGenError):
    """Raised when XML parsing fails (invalid structure, missing elements, etc.)."""

    pass


class CodeGenerationError(DataModelGenError):
    """Raised when code generation fails (template render, file write, etc.)."""

    pass


class ConfigurationError(DataModelGenError):
    """Raised when configuration is invalid or required config is missing."""

    pass
