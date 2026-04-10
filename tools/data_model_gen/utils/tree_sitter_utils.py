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
import re


def get_function_by_keywords(node, code_bytes, keywords=None):
    """Find all function definitions containing any of the keywords.

    :param node: The AST node to search from
    :param code_bytes: The source code as bytes
    :param keywords: The keywords to search for
    :returns: List of matching function nodes
    """
    results = []
    if node.type == "function_definition":
        decl_node = node.child_by_field_name("declarator")
        if decl_node:
            name = code_bytes[decl_node.start_byte:decl_node.end_byte].decode(
                "utf8", errors="ignore"
            )
            if any(keyword in name for keyword in keywords):
                results.append(node)

    for child in node.children:
        results.extend(get_function_by_keywords(child, code_bytes, keywords))
    return results


def extract_case_labels(node, code_bytes, regex_pattern=None):
    """Find all case statements and extract matching regex pattern.

    :param node: The AST node to search from
    :param code_bytes: The source code as bytes
    :param regex_pattern: The regex pattern to search for
    :returns: List of matching regex pattern
    """
    labels = []

    if node.type == "case_statement":
        src = code_bytes[node.start_byte:node.end_byte].decode(
            "utf8", errors="ignore"
        )
        matches = re.findall(regex_pattern, src)
        if matches:
            for match in matches:
                parts = match.split("::")
                if len(parts) >= 2 and "Id" in parts[-1]:
                    labels.append(parts[-2].lower())

    for child in node.children:
        labels.extend(extract_case_labels(child, code_bytes, regex_pattern))

    return labels
